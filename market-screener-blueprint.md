# Market Screener — Project Blueprint

**Classification:** Enterprise Market Data Microservice Engine  
**Build Type:** Cloud-Native Full-Stack Web Application  
**Target:** Internship Portfolio — Production-Ready Backend Engineering Showcase  
**Commitment:** 15–20 hours per week across 4 weeks

---

## What This Project Builds

A full-stack web application that replicates the core screening logic of tools like Streak — identifying stocks in a Stage 2 uptrend — and serves results through a clean browser-based dashboard. The screener pulls live market data for configurable stock universes, calculates moving averages, filters candidates, and presents them with market cap data in a filterable, sortable UI.

At the end of 4 weeks the entire system spins up with a single command and is interview-demonstrable in a live browser.

---

## The Screener Logic

The application filters stocks from a selected universe using the following condition chain:

```
Price > 50 DMA > 100 DMA > 150 DMA > 200 DMA
```

This is a **Stage 2 Uptrend** filter (Stan Weinstein framework). Each condition confirms a specific layer of bullish momentum:

| Condition | What It Confirms |
|---|---|
| Price > 50 DMA | Stock is above its short-term average — near-term momentum is bullish |
| 50 DMA > 100 DMA | Short-term trend above medium-term — momentum is accelerating |
| 100 DMA > 150 DMA | Medium-term trend above longer-term — sustained upward slope |
| 150 DMA > 200 DMA | Long-term trend is firmly rising — the structural base is solid |

A stock must satisfy all four conditions simultaneously to appear as a candidate.

---

## Supported Stock Universes

The application supports the following universes selectable from the dashboard UI:

| Universe | Description |
|---|---|
| NIFTY 50 | Top 50 large-cap stocks by market capitalisation |
| NIFTY 100 | Top 100 stocks — large cap |
| NIFTY 150 | Top 150 stocks — large and mid cap |
| NIFTY 200 | Top 200 stocks — large and mid cap |
| NIFTY 500 | Top 500 stocks — broadest general market index |

Universe lists are maintained as a single Python dictionary in `universes.py`. Adding a new universe in the future requires only a new key-value pair — all screener logic, API endpoints, and frontend dropdown pick it up automatically.

---

## Product Architecture

| Layer | Technology | Purpose |
|---|---|---|
| Data source | `yfinance` | Fetch OHLCV prices and market cap data from Yahoo Finance |
| Async runtime | `asyncio` + `asyncio.Semaphore` | Concurrent fetching with rate throttle protection |
| Database | PostgreSQL + `asyncpg` | Persist MA calculations and market cap snapshots |
| Backend API | FastAPI | Expose screener as REST endpoints with Swagger UI |
| Frontend | HTML + JS + CSS | Universe dropdown, filterable and sortable results table |
| Deployment | Docker + Docker Compose | One-command spin-up of all services |

### Why `yfinance`

- Free, no API key required
- Single function call returns a clean pandas DataFrame: `yf.download("RELIANCE.NS", period="1y")`
- Native NSE support via `.NS` ticker suffix
- Market cap accessible directly via `yf.Ticker("RELIANCE.NS").info["marketCap"]`
- Massive community support, minimal custom parsing needed

---

## Project File Structure

```
market-screener/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── fetcher.py          # yfinance async fetch logic + semaphore throttling
│   │   │   ├── screener.py         # MA calculation + Stage 2 filter logic
│   │   │   └── universes.py        # NIFTY universe ticker dictionaries
│   │   │
│   │   ├── db/
│   │   │   ├── models.py           # Table structure definitions
│   │   │   ├── queries.py          # All asyncpg query functions
│   │   │   └── migrations/
│   │   │       └── 001_init.sql    # Initial schema — tables + composite index
│   │   │
│   │   ├── api/
│   │   │   ├── routes.py           # FastAPI endpoint definitions
│   │   │   └── schemas.py          # Pydantic request/response models
│   │   │
│   │   ├── main.py                 # FastAPI app entry point
│   │   └── config.py               # Environment variable loader
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── index.html                  # Universe dropdown + results table UI
│   ├── app.js                      # Fetch API calls + table rendering + filter logic
│   ├── style.css
│   └── Dockerfile
│
├── docker-compose.yml              # Wires backend, frontend, and PostgreSQL together
├── .env.example                    # Template for environment variables (never commit .env)
├── .gitignore
└── README.md
```

### File Responsibility Summary

**`core/fetcher.py`** — all `yfinance` calls live here and nowhere else. Contains the async semaphore-guarded fetch loop that pulls price history and market cap for each ticker concurrently.

**`core/screener.py`** — pure logic file. Takes fetched data, computes the five moving averages, applies the Stage 2 filter chain, and returns a list of passing candidates with their metrics.

**`core/universes.py`** — a single Python dictionary mapping universe names to their NSE ticker lists. No logic, just data. This is the only file that needs touching when adding a new universe.

**`db/models.py`** — defines the schema structure for `stock_metrics` and `screening_runs` tables in code.

**`db/queries.py`** — all database read/write functions using `asyncpg`. No raw SQL anywhere else in the codebase.

**`db/migrations/001_init.sql`** — creates tables and the composite index on `(ticker, calculation_date)` that makes filtered queries fast.

**`api/routes.py`** — two core endpoints: `POST /api/v1/screen` triggers a background screening job; `GET /api/v1/candidates` retrieves stored results, optionally filtered by universe or market cap range.

**`api/schemas.py`** — Pydantic models that validate all inputs and outputs. Prevents bad data from entering the pipeline at the boundary.

**`main.py`** — mounts the router, sets up the database connection pool on startup, and runs the app.

**`config.py`** — reads from environment variables. DB connection string, semaphore concurrency limit, and any other runtime settings come from here, not from hardcoded values.

---

## User-Facing Features

### Universe Selection
The frontend dashboard presents a dropdown allowing the user to select which NIFTY universe to screen. On selection the frontend calls `POST /api/v1/screen` with the chosen universe and then fetches results via `GET /api/v1/candidates`.

### Results Table
Each candidate stock is displayed with the following columns:

| Column | Source |
|---|---|
| Ticker | Stock symbol |
| Company name | `yfinance` info |
| Current price | Latest close |
| 50 / 100 / 150 / 200 DMA | Computed and stored |
| Market cap | `yfinance` info, stored at fetch time |
| Market cap category | Derived: Large / Mid / Small cap |

### Market Cap Filtering
The user can filter the results table by market cap — either by category (Large / Mid / Small) or by a numeric range input — without triggering a new screening run. Filtering happens client-side in `app.js` against already-loaded data.

---

## 4-Week Sprint Schedule

| Week | Engineering Focus | Deliverable |
|---|---|---|
| 1 | Async concurrency and rate throttling | CLI script fetching 50+ tickers concurrently with visible semaphore state logs |
| 2 | PostgreSQL persistence layer | Schema live, composite index verified via `EXPLAIN ANALYZE`, async queries working |
| 3 | FastAPI REST layer | Swagger UI at `/docs`, POST triggers a background screen job, GET returns stored candidates |
| 4 | Docker and Compose orchestration | Single `docker-compose up --build` spins up all three services cleanly from scratch |

---

## Week-by-Week Engineering Breakdown

### Week 1 — High-Concurrency Data Harvesting

**Focus:** Replace blocking sequential data fetches with a non-blocking async pipeline using Python `asyncio` and `httpx.AsyncClient`. Integrate `yfinance` as the data source.

**Engineering mandate:**
- Implement `asyncio.Semaphore` with a configurable concurrency limit (default: 10) to prevent Yahoo Finance from rate-limiting or closing connections
- Each ticker fetch should be wrapped in error handling so a single failed ticker does not halt the entire pipeline
- Compute all five moving averages (50, 100, 150, 200 DMA + current price) and apply the Stage 2 filter in `screener.py`
- Fetch market cap alongside price data in the same call

**Key friction point:** Debugging unhandled exceptions inside `asyncio.gather` task lists without stopping the main pipeline. The pattern to learn is wrapping individual coroutines in `try/except` before passing them to `gather`, rather than catching at the top level.

**Week 1 sign-off:** Script executes 50+ watch requests concurrently. Console logs display semaphore acquire and release states. No blocking. No full pipeline halts on individual ticker errors.

---

### Week 2 — Relational Persistence Layer (PostgreSQL)

**Focus:** Move results from transient in-memory state into a durable PostgreSQL database accessible across sessions and API calls.

**Engineering mandate:**
- Design a normalised schema with at minimum a `stock_metrics` table storing: `ticker`, `universe`, `price`, `ma_50`, `ma_100`, `ma_150`, `ma_200`, `market_cap`, `calculation_date`
- Connect using `asyncpg` with a connection pool (not a single connection) — this is critical for concurrent API requests later
- Implement a composite index on `(ticker, calculation_date)` to make filtered queries performant
- Write all SQL as versioned migration files in `db/migrations/` — not inline strings scattered through the code

**Key friction point:** Managing connection pool lifecycle inside an async runtime. The pool must be created on app startup and closed on shutdown — not opened and closed per request. Also, tracking schema changes manually is tedious; establishing the migrations folder habit now prevents pain later.

**Week 2 sign-off:** Schema migration runs cleanly. `EXPLAIN ANALYZE` on a filtered ticker query shows index usage, not a sequential scan.

---

### Week 3 — RESTful Microservice Exposure (FastAPI)

**Focus:** Wrap the screening pipeline and database queries behind HTTP endpoints, making the system accessible over a network rather than only from the command line.

**Engineering mandate:**
- Expose `POST /api/v1/screen` — accepts a JSON body with `{ "universe": "NIFTY 500" }`, triggers Week 1 fetch and screen logic as a background task, returns a job acknowledgement immediately (non-blocking)
- Expose `GET /api/v1/candidates` — accepts optional query params for universe and market cap range, returns stored candidates from PostgreSQL
- Define Pydantic schemas for all request and response bodies in `schemas.py`
- Swagger UI at `/docs` must be live and functional

**Key friction point:** Preventing endpoint blocking during database lookups. All DB calls must use `await` with `asyncpg` — synchronous database calls inside an async endpoint will block the entire event loop. Also, path routing configuration in FastAPI requires understanding how `APIRouter` prefixes stack with `app.include_router`.

**Week 3 sign-off:** Swagger UI live at `/docs`. Triggering `POST /screen` populates database rows. `GET /candidates` returns them with correct filtering applied.

---

### Week 4 — Multi-Container Orchestration (Docker & Compose)

**Focus:** Eliminate "works on my machine" by containerising every service and wiring them together with Docker Compose.

**Engineering mandate:**
- Write a clean `Dockerfile` for the backend (`python:3.11-slim` base, install from `requirements.txt`, expose port 8000)
- Write a minimal `Dockerfile` for the frontend (serve static files via `nginx:alpine`)
- Write `docker-compose.yml` defining three services: `db` (official `postgres:15` image), `backend`, `frontend`
- The `db` service must use a named volume for data persistence across restarts
- The `backend` service must declare a health check dependency on `db` using `depends_on` with `condition: service_healthy`
- All secrets (DB password, DB name, DB user) must be injected via environment variables from `.env`, never hardcoded
- The `backend` service must run database migrations automatically on startup before accepting connections

**Key friction point:** Healthcheck timing between services. The `backend` starting before PostgreSQL is ready is the most common failure mode. The fix is a proper `pg_isready` healthcheck on the `db` service combined with `depends_on: condition: service_healthy` on the backend — not a fixed `sleep` hack.

**Week 4 sign-off:** Running `docker-compose down -v` followed by `docker-compose up --build` constructs the full stack, initialises the database schema, and serves the dashboard in a browser — no manual steps.

---

## Recruitment Code Quality Checkpoints

These are the specific things to demonstrate at each weekly checkpoint to confirm the work is interview-ready.

| Checkpoint | What to Show |
|---|---|
| End of Week 1 | Run the fetch script. Console shows concurrent semaphore acquire/release logs for 50+ tickers simultaneously. No sequential blocking visible. |
| End of Week 2 | Run `EXPLAIN ANALYZE SELECT * FROM stock_metrics WHERE ticker = 'RELIANCE' ORDER BY calculation_date DESC`. Output must show `Index Scan` not `Seq Scan`. |
| End of Week 3 | Open browser at `http://localhost:8000/docs`. Trigger POST `/screen` with a universe body. Switch to GET `/candidates` and confirm rows are returned. |
| End of Week 4 | From a clean state: `docker-compose down -v` then `docker-compose up --build`. Open browser. Dashboard loads. Screening runs. No manual database setup performed. |

---

## Environment Variables Reference

All runtime configuration is managed through environment variables. Copy `.env.example` to `.env` before running locally. Never commit `.env` to version control.

| Variable | Purpose | Example |
|---|---|---|
| `POSTGRES_USER` | Database user | `screener` |
| `POSTGRES_PASSWORD` | Database password | `changeme` |
| `POSTGRES_DB` | Database name | `market_screener` |
| `DATABASE_URL` | Full asyncpg connection string | `postgresql://screener:changeme@db:5432/market_screener` |
| `SEMAPHORE_LIMIT` | Max concurrent yfinance fetches | `10` |
| `BACKEND_PORT` | Port the FastAPI app listens on | `8000` |

---

## Database Schema

### Tables

#### `screening_runs`

Tracks every invocation of `POST /api/v1/screen`. The background task updates `status` as work progresses and writes `candidates_found` and `completed_at` on completion.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `universe` | `VARCHAR(20)` | NOT NULL | e.g. `NIFTY 50`, `NIFTY 500` |
| `status` | `VARCHAR(20)` | NOT NULL, default `pending` | `pending → running → completed → failed` |
| `candidates_found` | `INT` | nullable | Written on completion |
| `started_at` | `TIMESTAMP` | NOT NULL, default `now()` | |
| `completed_at` | `TIMESTAMP` | nullable | Null while job is in progress |

#### `stock_metrics`

Stores one row per passing candidate per screening run. `universe` is stored redundantly to allow fast single-table filtering on `GET /api/v1/candidates` without a join.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `run_id` | `UUID` | FK → `screening_runs(id)` ON DELETE CASCADE | |
| `ticker` | `VARCHAR(20)` | NOT NULL | NSE symbol e.g. `RELIANCE.NS` |
| `company_name` | `VARCHAR(100)` | nullable | From `yfinance` info |
| `universe` | `VARCHAR(20)` | NOT NULL | Redundant for query performance |
| `price` | `NUMERIC(12,2)` | NOT NULL | Latest close price |
| `ma_50` | `NUMERIC(12,2)` | NOT NULL | 50-day moving average |
| `ma_100` | `NUMERIC(12,2)` | NOT NULL | 100-day moving average |
| `ma_150` | `NUMERIC(12,2)` | NOT NULL | 150-day moving average |
| `ma_200` | `NUMERIC(12,2)` | NOT NULL | 200-day moving average |
| `market_cap` | `BIGINT` | nullable | From `yfinance` info, stored at fetch time |
| `cap_category` | `VARCHAR(10)` | nullable | Derived: `Large`, `Mid`, or `Small` |
| `calculation_date` | `DATE` | NOT NULL | Date the MAs were computed |
| `created_at` | `TIMESTAMP` | NOT NULL, default `now()` | |

### Indexes

| Index | Columns | Type | Purpose |
|---|---|---|---|
| `idx_stock_metrics_ticker_date` | `(ticker, calculation_date DESC)` | Composite B-tree | Week 2 checkpoint — makes `EXPLAIN ANALYZE` show `Index Scan` |
| `idx_stock_metrics_universe` | `(universe)` | B-tree | Fast filtering on `GET /api/v1/candidates?universe=...` |

### Migration SQL (`db/migrations/001_init.sql`)

```sql
CREATE TABLE screening_runs (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    universe         VARCHAR(20) NOT NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'pending',
    candidates_found INT,
    started_at       TIMESTAMP   NOT NULL DEFAULT now(),
    completed_at     TIMESTAMP
);

CREATE TABLE stock_metrics (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id           UUID         NOT NULL REFERENCES screening_runs(id) ON DELETE CASCADE,
    ticker           VARCHAR(20)  NOT NULL,
    company_name     VARCHAR(100),
    universe         VARCHAR(20)  NOT NULL,
    price            NUMERIC(12,2) NOT NULL,
    ma_50            NUMERIC(12,2) NOT NULL,
    ma_100           NUMERIC(12,2) NOT NULL,
    ma_150           NUMERIC(12,2) NOT NULL,
    ma_200           NUMERIC(12,2) NOT NULL,
    market_cap       BIGINT,
    cap_category     VARCHAR(10),
    calculation_date DATE         NOT NULL,
    created_at       TIMESTAMP    NOT NULL DEFAULT now()
);

CREATE INDEX idx_stock_metrics_ticker_date
    ON stock_metrics (ticker, calculation_date DESC);

CREATE INDEX idx_stock_metrics_universe
    ON stock_metrics (universe);
```

---

## Key Engineering Concepts to Understand Before Starting

Before touching any code, make sure the following concepts are clear — these underpin every week of the build.

**`asyncio` and the event loop** — Python runs one thread but can handle many tasks concurrently when tasks spend time waiting (on network, on disk). `await` yields control back to the event loop while waiting, letting other tasks run. This is how 500 ticker fetches run "at the same time" in a single process.

**`asyncio.Semaphore`** — a gate that allows only N coroutines through at once. Without it, 500 simultaneous HTTP requests to Yahoo Finance will get rate-limited or blocked. With a semaphore of 10, at most 10 fetches run at any moment; the rest wait their turn politely.

**Connection pooling** — opening a new database connection for every API request is slow and exhausts PostgreSQL's connection limit quickly. A connection pool maintains a fixed set of open connections and lends them out per request, returning them when done. `asyncpg.create_pool()` handles this.

**Composite index** — an index on two columns together: `(ticker, calculation_date)`. Queries filtering by both columns hit the index directly instead of scanning every row. This is what makes `EXPLAIN ANALYZE` show `Index Scan` instead of `Seq Scan`.

**Pydantic schemas** — FastAPI uses Pydantic models to validate that incoming request bodies match the expected shape and that response data is serialised correctly. Writing schemas in `schemas.py` and keeping them separate from route logic is an industry pattern that keeps the codebase clean.

**Docker networking** — each service in `docker-compose.yml` gets its own container and a shared internal network. The backend reaches the database not via `localhost` but via the service name `db` — Docker's internal DNS resolves it. This is why `DATABASE_URL` uses `@db:5432` rather than `@localhost:5432` in the container environment.
