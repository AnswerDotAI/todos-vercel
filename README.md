# todos-vercel

> *A sample FastHTML vercel app deployment*

This uses redis (via [tinyredis](https://github.com/AnswerDotAI/tinyredis)) as a simple DB for a basic todos app deployed to Vercel. To deploy it, create a Vercel KV database, fork this repo, and then when you deploy this repo as a Vercel project add these environment vars:

- `VERCEL_KV_URL`: The db URL provided by Vercel (or can be any redis provider URL)
- `SESSKEY`: A random uuid4 string, for example copied from https://www.uuidgenerator.net/version4
