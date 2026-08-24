# /backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import auth
import engine

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class OptionRequest(BaseModel):
    spot: float
    strike: float
    dte: float
    market_price: float
    option_type: str

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid quantum credentials vector.")
    token = auth.create_access_token(data={"sub": user})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/v1/calculate")
async def process_metrics(request: OptionRequest, token: str = Depends(oauth2_scheme)):
    iv = engine.solve_implied_volatility(request.market_price, request.spot, request.strike, request.dte, 0.07, request.option_type)
    delta, theta, vega = engine.calculate_black_scholes_greeks(request.spot, request.strike, request.dte, 0.07, iv, request.option_type)
    return {"iv": iv, "delta": delta, "theta": theta, "vega": vega}
