This confirms the vulnerability. The docs at `docs/usage/webhooks.md` explicitly state `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (line 125) — but the verification only covers the raw body, not the `shop`, `topic`, `api_version`, or `webhook_id` fields that are trusted and passed straight to the handler via `WebhookMetadata`.This confirms the full chain: `Webhooks::Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`), so the HMAC in `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) only binds the body bytes to the secret — it never covers `shop`, `topic`, `webhook_id`, or `api_version`, which are read straight from attacker-controllable HTTP headers (`shopify_header`, `lib/shopify_api/webhooks/request.rb:67-70`) and then trusted unconditionally by `Registry.process` to build `WebhookMetadata` (`lib/shopify_api/webhooks/registry.rb:188-199`), which the host app's handler uses to attribute/act on data per-shop (`docs/usage/webhooks.md:10-17,125`).

### Title
Webhook shop/topic identity spoofing via unsigned headers — HMAC only covers the body, not shop-domain or topic - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before invoking the app's handler, but the HMAC signature computed by `Utils::HmacValidator` only ever signs the raw request body (`Webhooks::Request#to_signable_string` returns `@raw_body`). The `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from HTTP headers and delivered unverified to the app's handler as `WebhookMetadata` — are not part of the signed payload at all.

### Finding Description
The identity binding the library implies (and documents) is: `hmac == HMAC(secret, request)` authenticates that "this webhook, for this shop/topic, came from Shopify." In reality the binding enforced is only:

`hmac == HMAC(secret, raw_body)`

while `shop`, `topic`, `webhook_id`, `api_version` are read from headers with zero cryptographic linkage to that signature: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

Since a legitimate `Content-Length`-analog check (the HMAC) validates the *body bytes* but the app *acts on* separate unauthenticated fields (`shop-domain`, `topic` headers), any entity able to produce one valid `(raw_body, hmac)` pair for the app's shared `api_secret_key` — e.g., a merchant who has installed the app and can trigger/observe a real webhook delivery to their own endpoint, since Shopify apps use a single `client_secret` shared across all installing shops, not a per-shop secret — can replay that exact body+signature to the app's webhook endpoint while forging the `x-shopify-shop-domain` and/or `x-shopify-topic` headers to arbitrary values. `Registry.process` will accept it as valid (the body HMAC checks out) and hand the handler a `WebhookMetadata` claiming the forged shop/topic, per the documented handler contract.

### Impact Explanation
This breaks the per-tenant trust boundary the gem is expected to enforce: a webhook payload legitimately produced under one merchant's shop can be attributed to a different, victim shop. Any host application that uses `data.shop` (as instructed in `docs/usage/webhooks.md`) to key persistence, cache invalidation, or business logic per-tenant will process attacker-chosen body content under the victim's tenant identity — a cross-tenant data-integrity/confusion vector, without needing the `api_secret_key`, an access token, or any privileged access beyond ordinary use of the shared app.

### Likelihood Explanation
Any shop that installs the app already shares the same `client_secret`/`api_secret_key` used for HMAC computation (this is standard Shopify app architecture — the secret is per-app, not per-shop). An installer merely needs to trigger any webhook topic they've subscribed to and capture the outbound request's raw body and `X-Shopify-Hmac-Sha256` header (e.g., via their own reverse proxy/logging in front of their receiving endpoint), then resend it directly to the target application's public webhook endpoint with modified `X-Shopify-Shop-Domain`/`X-Shopify-Topic` headers. No secret material needs to be extracted or brute-forced.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` (or at minimum `shop` and `topic`) into the signed material checked by `HmacValidator`, or otherwise require the host application to cross-check `data.shop` against an already-authenticated session before trusting it. At minimum, document explicitly that `data.shop`/`data.topic` are unauthenticated header values and must never be trusted as tenant identifiers without additional verification (e.g. checking against a known/registered shop record) — since the current docs (`docs/usage/webhooks.md:10-17`) present them as reliable, verified webhook metadata.

### Proof of Concept
1. App AttackerCo installs the target Shopify app on `attacker.myshopify.com`, sharing the same `api_secret_key` as every other installer.
2. AttackerCo triggers a subscribed webhook (e.g. `orders/create`) with attacker-chosen order data, and captures the raw POST body plus the `X-Shopify-Hmac-Sha256` header sent by Shopify to their registered endpoint.
3. AttackerCo POSTs that exact `(raw_body, hmac)` pair to the target app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and keeps/changes `X-Shopify-Topic` as desired.
4. `Webhooks::Request.new` accepts the forged headers (`lib/shopify_api/webhooks/request.rb:45-63`), `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only recomputes HMAC over `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. The app's handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and processes/stores the attacker's data under the victim's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
