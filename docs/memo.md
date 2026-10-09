# Memo: Where Detroit should act on slow 311 requests

To: whoever runs field operations and 311 service delivery for the City of Detroit
From: Gunnar Austin
Data: Improve Detroit Issues, requests created June 30, 2024 through September 28, 2026

I do not work for the city and the data has no department, crew or staffing field. I inferred who owns each request type from its name, so treat the owners below as a starting guess for the city to confirm. Everything else is counted from the data. The numbers come from `python src/memo_numbers.py` and `python src/findings.py`.

## The ask

1. **Staff up for May through August, starting with Illegal Dumping and Debris.** The summer drop is not a volume surge. It is a capacity gap, and for dumping it is a stall.
2. **Clear the 784 requests that have been open more than 90 days, owner by owner.** Three categories hold 78% of them.
3. **Look at curbside Solid Waste in District 4 first.** It explains most of why District 4 is slowest.

## 1. Seasonal staffing: Grass and Weeds, Illegal Dumping and Debris

Grass and Weeds closed 95.0% of requests within 30 days in the 12 months before September 2025 and 69.8% in the latest 12. Illegal Dumping and Debris went from 83.2% to 66.7%. Together they are 8,075 of the 13,571 requests in the latest 12 months that missed the 30 day window (60%).

The decline sits in one season. Here is the 30 day close rate by creation month.

| Month created | Grass 2025 | Grass 2026 | Dumping 2025 | Dumping 2026 |
|---|---:|---:|---:|---:|
| May | 96.2% | 49.0% | 70.2% | 49.9% |
| June | 93.4% | 32.8% | 73.7% | 31.8% |
| July | 95.3% | 84.7% | 71.0% | 45.5% |
| August | 92.8% | 78.2% | 75.7% | 42.2% |

Volume did not cause it. Grass requests in May and June were 1,156 and 1,640 in 2025 and 1,205 and 1,682 in 2026. Dumping ran 1,480, 1,752, 2,237 and 2,109 from May through August 2026 against 2,321, 1,720, 2,372 and 1,845 a year earlier, so no clear rise. More work did not arrive. The same work was handled slower.

The two categories behave differently, so they need different fixes.

**Grass and Weeds is late, not abandoned.** May and June 2026 requests had 86.8% and 88.9% closed by day 60, and the median days to close went from 5 and 9 in 2025 to 29 and 33. Almost nothing is still open. Demand is also sharply seasonal: 1,100 to 1,800 requests a month from May through September, and 107 or fewer a month from December through March. That is a case for crews or mowing contracts that are in place by May 1, not for a year round headcount.

**Illegal Dumping and Debris is stalling.** By day 60 only 76.7% of June 2026 requests had closed, against 88.2% for June 2025, and 4.9% are still open against 0.6% (the 2025 cohort has had a year longer to clear, so that second comparison flatters 2025). Dumping also ran 70% to 76% in the summer of 2025, so even the 2025 level is a floor to beat and not a target.

Size of the gap, measured against the city's own 2025 rate for the same month:

- Grass and Weeds: about 2,000 more requests missed the 30 day window in May through August 2026 than 2025 service levels would have allowed.
- Illegal Dumping and Debris: about 2,300 more.

I cannot turn that into a headcount. That needs crew productivity and route data the city has and I do not. What the data supports is when (April through August), where the gap is (these two categories) and how big (about 4,300 requests in one summer).

## 2. The 784 requests open more than 90 days

"Open" here means status Open or Acknowledged, aged from the newest request in the data. There are 5,068 open, and 784 are older than 90 days.

| Category | Over 90 days | Share |
|---|---:|---:|
| Illegal Dumping and Debris | 259 | 33% |
| Vacant Property and Code | 200 | 26% |
| Traffic Signs and Signals | 154 | 20% |
| Everything else (12 categories) | 171 | 22% |

They cluster by district too:

- **Illegal Dumping and Debris** is spread out, with Districts 5 (49), 3 (44) and 7 (42) the highest. It needs a citywide sweep, not a district fix.
- **Vacant Property and Code** is concentrated. Districts 4 (55) and 3 (52) hold 107 of the 200. The types are squatter reports, reboard requests and similar, which look like building enforcement and not public works.
- **Traffic Signs and Signals** is concentrated in District 5 (46), District 7 (30) and requests with no district (41). That is 117 of 154. Sign and signal work usually waits on a specialist crew, so the owner is likely a traffic engineering group.

A one time push on 784 requests is small next to the 209,394 in the data, but these are the ones residents have waited more than a quarter of a year on. I would hand each owner its own list and ask for a status on every one, including a "cannot do" with a reason. Part of this backlog may be requests that were fixed and never marked closed. I cannot tell that from the status field. A review would separate stale records from real work.

## 3. District 4 at 79.9%

District 4 closes 79.9% of its requests within 30 days, the lowest of any district. It was 87.0% a year earlier, a drop of 7.0 points. District 3 is next at 81.0%. The citywide rate is 84.8%.

Request mix does not explain it. If District 4 had closed each category at the citywide rate for that category, it would have closed 83.9%. It is about 4 points below that, roughly 557 requests over the year. Three categories account for almost all of it:

| Category | District 4 rate | Citywide rate | Requests behind the gap |
|---|---:|---:|---:|
| Solid Waste and Recycling | 64.8% | 80.2% | 382 |
| Illegal Dumping and Debris | 63.8% | 66.7% | 86 |
| Grass and Weeds | 64.5% | 69.8% | 62 |

Solid Waste and Recycling is two thirds of the District 4 gap by itself. It covers curbside pickup problems and recycling cart requests. District 4 files 2,481 of them in the year, so a small improvement is worth a lot. I would start there with the DPW routes that serve the district, and treat the dumping and grass gaps as part of the citywide summer problem in section 1.

## What this memo cannot tell you

- **The data records when a request was marked closed, not whether the problem was fixed.** A faster close rate could be faster work or faster paperwork.
- **The September 2024 step.** Requests created before September 2024 closed at about half the later rate, which looks like a change in how the city closes or archives requests. All comparisons here start at September 2024. I do not know the cause.
- **Two summers is not a trend.** The 2026 drop could be a real slowdown, a change in closing practice, or a one season staffing problem. I would want the city to say which before acting on the size of the gap.
- **Owners are guessed from request names.** Several types are labeled for internal use ("DPW ONLY", "BSEED USE ONLY") and the city can place them better than I can.
- **5.9% of requests have no council district.** They are in the citywide numbers and left out of the district ones. They show up in the Traffic Signs and Signals count above.
- **The layer is live.** A later pull will not match these counts exactly.

## What I would check next

Find out what changed in the closing process around September 2024. Pull the same data for 2022 and 2023 to see whether the May to August dip in dumping is a permanent seasonal pattern. Ask the city for the owning department on each request type, so section 2 can name owners and not guess them.
