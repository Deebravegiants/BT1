Confirmed root cause: the webhook HMAC signature covers only the raw request body, while the `shop`, `topic`, and `webhook_id` values used for routing/processing come from unauthenticated HTTP headers. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook HMAC only signs the request body, letting an attacker swap the `shop`/`topic`/`webhook_id` headers without invalidating the signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verified by `Utils::HmacValidator.validate` in `Registry.process` binds nothing but the JSON body. The `shop`, `topic`, `api_version`, and `webhook_id` values are parsed straight from HTTP headers and handed to the app's handler without ever being part of the signed material.

### Finding Description
`Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [4](#0-3) 

and `Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [5](#0-4) 

`request.shop`/`request.topic`/`request.webhook_id` are read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` (and topic/webhook-id) headers via `shopify_header`:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [6](#0-5) 

`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received `hmac`: [3](#0-2) 

Because the signable string is only the raw body, **the binding "HMAC covers all fields the handler trusts" does not hold**: `HMAC(raw_body) == HMAC(raw_body)` is satisfied even when `shop`/`topic`/`webhook_id` headers are altered, since these headers are never mixed into the signed bytes. Any party who legitimately receives a valid `(raw_body, hmac)` pair for one shop — e.g., a merchant who installs the app in their own store and triggers a webhook-generating event — can replay that exact body/HMAC pair while substituting the `shop-domain` header for a different (victim) shop. `Registry.process` will still validate the HMAC successfully and will invoke the app's handler with `data.shop` set to the attacker-chosen victim shop while `data.body` is the attacker's own content.

### Impact Explanation
This breaks the identity binding between the authenticated bytes (the body) and the tenant identifier (`shop`) that the host application relies on to attribute webhook data to the correct merchant. Any app built on `shopify_api` that uses `data.shop` from `WebhookMetadata` to select which tenant's records to update (a documented and expected usage pattern — see `docs/usage/webhooks.md`) can be tricked into writing/mutating data associated with a shop the attacker does not control, using a signature that was never computed over that shop identifier. This is a cross-tenant data-integrity/confusion issue reachable by any user who can install the app on their own store (or otherwise obtain one legitimate webhook body+HMAC) and replay it against the app's webhook endpoint with a forged `shop-domain` header — no access token, `client_secret`, or privileged credential is required.

### Likelihood Explanation
Likelihood is Medium-to-High: the attacker only needs (1) their own legitimate install to receive a real `(body, HMAC)` pair for an event of their choosing, and (2) the ability to POST to the app's public webhook endpoint with modified headers — both of which are available to any unprivileged internet user/merchant. No secret key or brute forcing of the HMAC is needed.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the material that is HMAC-signed/verified (or otherwise cryptographically bind them, e.g., by validating that the request's `shop` header matches a shop already known/expected for this delivery), instead of validating the HMAC over the raw body alone in `Request#to_signable_string`.

### Proof of Concept
1. Merchant A installs the app on `shop-a.myshopify.com` and triggers an `orders/create` webhook. Shopify sends a legitimate request with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC(api_secret_key, B)`.
2. The attacker (Merchant A) intercepts/replays this request to the app's public webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a different, victim shop that also uses the app).
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only returns `B`, matching `H`.
4. The app's handler is invoked with `data.shop == "shop-b.myshopify.com"` and `data.body` containing attacker-controlled order data from `shop-a`, even though this content was never signed for `shop-b`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
