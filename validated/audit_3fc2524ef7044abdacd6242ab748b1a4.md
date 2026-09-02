# Zero-Value-Style Identity Binding Bypass in Webhook Verification — `shop` (and `topic`/`webhook_id`) Headers Are Trusted But Not Covered by the HMAC

### Title
Webhook `shop` domain is trusted from an unauthenticated header while only the raw body is bound to the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, and `webhook_id` purely from HTTP headers, while `to_signable_string` (the value actually protected by the HMAC signature) returns only the raw request body. `Registry.process` validates the HMAC and then unconditionally hands the caller-supplied `shop` header value to the app's webhook handler as if it were an authenticated identity. This breaks the identity binding: `hmac_valid == true` should imply the whole delivery (including which shop it is attributed to) is authentic, but in fact only the body bytes are authenticated — the `shop` (tenant identifier) is not.

### Finding Description
`Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb` returns `@raw_body` only: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are read straight from headers, completely outside of what is signed: [2](#0-1) 

`HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (the body): [3](#0-2) 

`Registry.process` checks only that HMAC, then immediately forwards the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` to the app's handler as trusted identity data: [4](#0-3) 

The equality this design implicitly (and incorrectly) assumes is:
`hmac_valid(body, secret) == true` ⇒ `shop header is authentic for this body`

But the real invariant enforced by the code is only:
`hmac_valid(body, secret) == true` ⇒ `body bytes are authentic`

Since `shop`, `topic`, and `webhook_id` live entirely in headers that are never mixed into the signable string, any request carrying a *previously observed, validly-signed body* (paired with its real HMAC) can have its `shop-domain`/`topic`/`webhook-id` headers freely rewritten by anyone who can reach the app's public webhook endpoint, and the signature check in `Registry.process` will still pass.

### Impact Explanation
An unprivileged internet user can:
1. Install the target app on their own (attacker-controlled) development/free shop — no privileged credentials needed, this is standard app-install flow available to anyone.
2. Trigger a webhook delivery for that shop (e.g., `orders/create`) and capture the raw body + `X-Shopify-Hmac-Sha256` header — both are visible to the attacker's own endpoint or interceptable since they own that shop's data.
3. Replay that exact `(raw_body, hmac)` pair to the victim app's webhook endpoint, but with `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) headers changed to point at a **different, victim shop**.
4. `Utils::HmacValidator.validate` still succeeds (it only re-hashes the body), so `Registry.process` dispatches the handler believing the event legitimately originates from the victim shop.

Depending on what the app does with `WebhookMetadata#shop` (e.g., updating per-shop data, triggering fulfilment/order-processing side effects, writing to a per-tenant record keyed by `shop`), this enables cross-tenant data injection/corruption attributed to a shop the attacker does not own or control — a cross-tenant access primitive per the impact categories in scope.

### Likelihood Explanation
Exploitation requires only: (a) the ability to install the target app on any shop (freely available to any developer/unprivileged user via a Shopify Partner/dev store), and (b) network access to the app's public webhook endpoint to replay a modified request — both trivially available to an "unprivileged internet user." No access to `api_secret_key`, tokens, or any Shopify-internal secret is required, since the attacker reuses a genuinely signed body/HMAC pair they legitimately obtained for their own shop.

### Recommendation
Bind the tenant/topic identity into the value that is actually verified, or otherwise cryptographically tie the trusted headers to the signature, e.g.:
- Extend `to_signable_string` (or add a secondary verification step) to include `shop`, `topic`, and `webhook_id` alongside the raw body before computing/comparing the HMAC, so any header tampering invalidates the signature.
- At minimum, document/enforce that `WebhookMetadata#shop` must be cross-checked by the app against its own known/installed shop list before being trusted, and consider raising in `Registry.process` if the header-derived `shop` cannot be corroborated.

### Proof of Concept
```
# Attacker owns shop A, installs the app, and receives a legitimate webhook:
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <valid-hmac-of-raw-body>
X-Shopify-Shop-Domain: shop-a.myshopify.com
Body: {"id": 1, "malicious_field": "..."}

# Attacker replays the identical body + hmac, but swaps the shop header:
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <same-valid-hmac-of-raw-body>   # unchanged, still verifies
X-Shopify-Shop-Domain: victim-shop.myshopify.com        # forged
Body: {"id": 1, "malicious_field": "..."}

# ShopifyAPI::Webhooks::Registry.process(request) validates the HMAC against
# `raw_body` only (lib/shopify_api/webhooks/request.rb#to_signable_string),
# succeeds, and calls the handler with `shop: "victim-shop.myshopify.com"`.
```

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
