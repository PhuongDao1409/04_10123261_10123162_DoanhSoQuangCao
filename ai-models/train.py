
import os, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

url = "https://raw.githubusercontent.com/selva86/datasets/master/Advertising.csv"
print(">>> Ðang t?i d? li?u t?:", url)
df = pd.read_csv(url)
if "Unnamed: 0" in df.columns: df = df.drop(columns=["Unnamed: 0"])
df.columns = [c.strip().capitalize() for c in df.columns]
if "Tv" in df.columns: df.rename(columns={"Tv": "TV"}, inplace=True)

X, y = df[["TV", "Radio", "Newspaper"]], df["Sales"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

models = {
    "linear": LinearRegression(),
    "ridge": Ridge(alpha=1.0),
    "random_forest": RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42),
    "xgboost": XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
}

os.makedirs("models", exist_ok=True)
for name, model in models.items():
    pipe = Pipeline([("scaler", StandardScaler()), ("model", model)])
    pipe.fit(X_train, y_train)
    joblib.dump(pipe, f"models/{name}.joblib")
print(">>> ÐÃ T?O XONG 4 FILE .JOBLIB THÀNH CÔNG! <<<")

