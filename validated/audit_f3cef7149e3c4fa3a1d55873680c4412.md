### Title
Webhook shop-domain header is not covered by HMAC validation, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, but the `shop` (tenant) identity that the handler acts on is read from an HTTP header that is never included in the signed bytes. Because the app's webhook signing secret (`Context.api_secret_key`) is shared across every shop that has the app installed, any merchant who installs the app can obtain a validly-signed `(body, hmac)` pair and replay it to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header naming a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` only checks that the received HMAC matches `HMAC(secret, verifiable_query.to_signable_string)`: [3](#0-2) 

`Registry.process` uses this HMAC check as the sole authentication step, then trusts `request.shop` (parsed straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) to build `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop domain verified by the signature` == `shop domain the handler acts on`. Here the signature covers only the body, so this equality does not hold — the `shop` value used for tenant attribution is completely outside the authenticated data.

Because the app's `client_secret`/webhook secret is per-app, not per-shop, any account holder who has the app installed on their own shop can:
1. Trigger a webhook delivery to their own endpoint and capture the raw body + its valid `x-shopify-hmac-sha256` value (both computed with the app's single shared secret).
2. Replay that exact `(body, hmac)` pair directly to the app's public webhook endpoint, substituting `x-shopify-shop-domain` with an arbitrary victim shop's domain (and, if desired, `x-shopify-topic`, which is likewise unauthenticated).
3. `HmacValidator.validate` succeeds because the body/hmac pair is genuinely valid; `Registry.process` then dispatches the handler with `shop: <victim shop>` even though the victim's own store never sent this event.

### Impact Explanation
This breaks tenant isolation: an app built on this gem cannot distinguish "this webhook event genuinely originated from shop X" from "an unrelated account replayed a self-obtained signature while claiming to be shop X." Any host application that keys persistence, authorization, or side effects (order/inventory updates, GDPR data requests, uninstall handling, etc.) off `WebhookMetadata#shop` is exposed to cross-tenant data injection/corruption purely because the SDK never binds `shop` into the authenticated payload.

### Likelihood Explanation
Any user who can install the target app on a shop they control (a normal, unprivileged step available to any merchant) can capture one legitimate `(body, hmac)` pair and freely target any other shop by forging the header on a directly-crafted HTTP request to the app's public webhook URL — no secrets, tokens, or victim cooperation are required.

### Recommendation
Do not rely solely on body HMAC for tenant attribution. Either:
- Include `shop`, `topic`, and `webhook_id` in the signed/verified material (e.g., verify against an expected shop registered for that webhook subscription), or
- After HMAC validation, require the caller to supply/confirm the expected shop (e.g., look up an active session/webhook registration for `request.shop` and reject if the shop wasn't the one that owns the subscription that triggered delivery), so `request.shop` can never be trusted purely on the strength of the body signature.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com"
# and receives a real webhook delivery with a genuine signature:
raw_body = '{"id": 1, "note": "any body attacker can influence or simply capture"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SHARED_SECRET, raw_body)
)

# Attacker replays it directly to the app's public webhook endpoint,
# forging the shop header to target a victim shop they don't control:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate succeeds (body/hmac genuinely match),
#    handler.handle is invoked with WebhookMetadata#shop == "victim-shop.myshopify.com"
``` [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```
