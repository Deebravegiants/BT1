[File: src/backend/presigned_url.rs -> Scope: Critical] [Function: request] On an error response, `presigned_url::request` calls `response.text().await?` and logs the full body via `tracing::error!(\
