### Title
Webhook `shop`, `topic`, and `webhook-id` are trusted from unauthenticated HTTP headers while only the raw body is HMAC-verified - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature (`to_signable_string`) over the raw request body only, but the `shop`, `topic`, `api_version`, and `webhook_id` values that the registry dispatches on and hands to the app's handler are read straight from HTTP headers that are never included in the signed material.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 
while `shop`, `topic`, `webhook_id`, and `api_version` are all parsed out of headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only the body HMAC via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` and `request.topic` to route to a handler and construct `WebhookMetadata`: [3](#0-2) 

`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the received signature — since `to_signable_string` for webhooks is just the body, the header fields are structurally outside the equality the HMAC is supposed to enforce: [4](#0-3) 

This is exactly the identity-binding break the report's bug class describes: a field acted on (`shop`) is not covered by the authenticator (HMAC) that is supposed to prove the tenant identity. Because an app owner/developer can legitimately install their own app on their own shop, they can capture a genuine `(raw_body, hmac)` pair that Shopify computed with the real `client_secret` for their own tenant, then replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a different, victim shop. `HmacValidator.validate` will still succeed because it only checks the body bytes, and `Registry.process` will hand the attacker-controlled body to the handler tagged with the victim's shop domain — i.e., `shop authenticated ≠ shop the data is attributed to`.

### Impact Explanation
This is a cross-tenant data-injection primitive: an app that persists webhook payloads keyed by `WebhookMetadata#shop` (a normal, documented usage pattern) can be made to write/associate attacker-supplied body content under another merchant's shop domain, without the attacker ever possessing that merchant's or the app's `client_secret`. Depending on what the handler does with the body (e.g., updating order/inventory records, redact processing, GDPR compliance handlers), this can corrupt another tenant's data or trigger tenant-scoped side effects using forged input — a cross-tenant boundary violation, which the rules classify as Critical impact.

### Likelihood Explanation
Requires only that the attacker control one shop where the app is installed (an ordinary "unprivileged internet user" relative to the victim tenant) and be able to POST an arbitrary HTTP request with custom headers to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is needed. The library performs no host/header authentication beyond the body HMAC, so the replay is trivial once a legitimate `(body, hmac)` pair for the attacker's own shop is captured.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`) in the signed material that `to_signable_string` produces, or otherwise bind them cryptographically to the HMAC (e.g., verify against a value obtained independently, such as a lookup keyed by webhook-id via the Admin API), so that `HmacValidator.validate` cannot pass while an attacker has substituted the shop/topic headers on a replayed, differently-attributed body.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`) with a body they fully control (order note, custom attributes, etc.).
2. Shopify delivers the webhook to the app's callback URL with headers `X-Shopify-Hmac-Sha256: <valid hmac of body>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Attacker captures this raw request (raw body + `X-Shopify-Hmac-Sha256` value) and replays it directly to the same callback URL, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com`:
   ```ruby
   headers = {
     "x-shopify-topic" => "orders/create",
     "x-shopify-hmac-sha256" => captured_hmac_base64,   # unchanged, still valid for raw_body
     "x-shopify-shop-domain" => "victim.myshopify.com",  # forged
   }
   request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: headers)
   ShopifyAPI::Webhooks::Registry.process(request)  # passes HMAC check, handler invoked with shop: "victim.myshopify.com"
   ```
4. `Utils::HmacValidator.validate(request)` returns `true` because it only re-hashes `captured_raw_body`, at [5](#0-4) . The registered handler then executes with `WebhookMetadata.shop == "victim.myshopify.com"` and `body == captured_raw_body`, an attacker-controlled payload attributed to a tenant the attacker does not control.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
