from fastapi import FastAPI
from starlette.responses import HTMLResponse

from model.CutSolver import distribute
from model.Job import Job, Result

app = FastAPI()


# response model ensures correct documentation
@app.post("/solve", response_model=Result)
def solve(job: Job):
    assert job.__class__ == Job

    print(f"Got job with length {len(job)}")

    solved = distribute(job)

    return solved


# content_type results in browser pretty printing
@app.get("/", content_type=HTMLResponse)
def index():
    # TODO: redirect to docs
    return "Hello FastAPI!"


@app.get("/about", content_type=HTMLResponse)
def about():
    text = 'Visit <a href="https://github.com/ModischFabrications/CutSolver">' \
           'the repository</a> for further informations.'
    return text


# for debugging only
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)