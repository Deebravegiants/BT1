## Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated headers while the HMAC only covers the raw body - Cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying field `shop` (along with `topic` and `webhook_id`) from HTTP headers that are **not** included in the HMAC signature check. `Utils::HmacValidator` only ever verifies the raw request body against the shared `api_secret_key`. Because the signature never binds `shop` to the body, any party who has previously received one genuine, signed webhook for their own store can replay that exact body+HMAC pair to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` header, and the app will process the payload as if it came from a different shop.

### Finding Description
`Webhooks::Registry.process` verifies authenticity solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for a webhook `Request`, `to_signable_string` returns only the raw JSON body — never the headers: [2](#0-1) 

Yet the same `Request` object exposes `shop`, `topic`, and `webhook_id`, all parsed straight from headers with no cryptographic binding to those header values: [3](#0-2) 

After the HMAC check passes, `Registry.process` immediately hands `request.shop` — the unauthenticated header value — to the app's handler as the tenant identity for the event: [1](#0-0) 

Because the app-wide `api_secret_key` (the HMAC key) is identical for every shop that installs the app, and the HMAC is computed only over the body, a valid `(body, hmac)` pair captured from a webhook genuinely sent for shop A remains a valid `(body, hmac)` pair no matter what `x-shopify-shop-domain` header accompanies it. `HmacValidator.validate_signature` uses `OpenSSL.secure_compare` correctly for the bytes it checks, but the bytes it checks (`body`) are not the bytes the application trusts as the shop identity (`headers["shop-domain"]`) — this is exactly the "bytes verified versus bytes parsed" mismatch: the equality the code implicitly assumes, `hmac_verified_body == shop_bound_to_that_body`, does not hold.

### Impact Explanation
This breaks the tenant boundary (cross-tenant access), which is listed as a Critical impact. An attacker who is merely an ordinary (unprivileged) installer/user of the app on their own store can:
1. Trigger or wait for a legitimate webhook to be delivered to their app instance for their own shop (e.g. `orders/create`), capturing the raw body and its valid `x-shopify-hmac-sha256`.
2. Replay that exact body and HMAC header to the app's webhook endpoint, but with the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header rewritten to name a *different* shop that also uses the app.
3. `HmacValidator.validate` still succeeds (it only checks the body), so `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: <attacker-chosen shop>, body: <attacker's own captured body>, ...)`.

Any app logic that uses `request.shop` to select which tenant's session/data store to write to (a very common and encouraged pattern, since `WebhookMetadata#shop` is the field this gem hands developers precisely for that purpose) can be tricked into writing or acting on attacker-supplied data under another merchant's identity.

### Likelihood Explanation
Exploitation requires no credentials, tokens, or privileged access — only that the attacker operates their own installation of the target app (which is normal, unprivileged use) and can send arbitrary HTTP requests to the app's public webhook endpoint. Capturing one's own legitimately-signed webhook body/HMAC is trivial and guaranteed to happen during normal app usage.

### Recommendation
Bind the identity fields to the authenticated payload instead of trusting header values independently of the signature:
- Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC validation (mirroring how `Oauth::AuthQuery#to_signable_string` folds `shop`, `host`, etc. into the signed string), or
- After successful HMAC validation, cross-check `request.shop` against an independently-known value (e.g. the shop associated with the specific `webhook_id`/subscription via the Admin API) before dispatching to the handler, and document clearly that `request.shop` is not itself authenticated by the HMAC check.

### Proof of Concept
1. App installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, sharing one `api_secret_key`.
2. Shopify sends attacker a genuine webhook:
```
POST /webhooks
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <valid-for-body>
x-shopify-shop-domain: attacker-shop.myshopify.com
x-shopify-webhook-id: w-1
Body: {"id": 1, "note": "malicious payload"}
```
3. Attacker replays the identical body and `x-shopify-hmac-sha256` value, only changing the shop header:
```
POST /webhooks
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <same-valid-hmac>
x-shopify-shop-domain: victim-shop.myshopify.com
x-shopify-webhook-id: w-1
Body: {"id": 1, "note": "malicious payload"}
```
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully (`lib/shopify_api/webhooks/request.rb:45-63`), `Utils::HmacValidator.validate` returns `true` because it only rehashes the body (`lib/shopify_api/utils/hmac_validator.rb:26-31`), and `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-199`) even though Shopify never sent this event for that shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
