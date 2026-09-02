### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, but the `shop` value that is subsequently trusted and handed to the app's webhook handler is read from an HTTP header that is never part of the signed payload. Any actor who can obtain one validly-signed webhook (e.g., by installing the app on their own store, which any unprivileged internet user can do) can replay that exact body/HMAC pair while substituting the `x-shopify-shop-domain` header for an arbitrary victim shop, and the gem will accept it as an authentic webhook for the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop` from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 

But the signable string used for HMAC verification is built only from the raw request body: [2](#0-1) 

`HmacValidator.validate` computes the HMAC over `to_signable_string` (the raw body) and compares it to the `hmac-sha256` header — it never touches the shop header: [3](#0-2) 

`Registry.process` only checks this body-only HMAC before dispatching to the topic handler, passing `request.shop` straight through as the tenant identity for the webhook: [4](#0-3) 

The equality the gem implicitly (and incorrectly) assumes is:
`shop_attributed_to_webhook (from unauthenticated header) == shop_that_actually_generated_the_signed_body`

Because the HMAC only binds the body bytes, and the app's `api_secret_key` (client secret) is shared across every shop that installs the app — not per-shop — a webhook that Shopify genuinely signs for one store (e.g., the attacker's own free/dev store) remains validly signed no matter which shop-domain header is attached to it. An attacker can therefore trivially forge the shop identity while keeping cryptographic validity intact, breaking the tenant-isolation boundary that `HmacValidator.validate` is supposed to enforce.

### Impact Explanation
This allows cross-tenant action: an unprivileged user who installs the app on their own store receives genuinely signed webhooks (any topic, including sensitive ones like `app/uninstalled` or `customers/redact`). By replaying the body+HMAC with the `shop-domain` header rewritten to a victim's shop, the attacker gets the app to execute handler logic (session deletion, data redaction, business logic tied to shop identity, etc.) attributed to the victim tenant, without ever needing the victim's credentials, access token, or `api_secret_key`. This matches the "cross-tenant access" Critical impact category, since the tenant boundary enforced by the webhook HMAC is not actually binding the identity field that downstream code trusts.

### Likelihood Explanation
Likelihood is high for any attacker who can install the target app on a store they control (a standard, low-barrier action for public/unlisted Shopify apps), since no secret material or privileged access is required — only the ability to capture one legitimate webhook delivery and replay it with a modified header to the app's own public webhook endpoint.

### Recommendation
Bind the shop identity into the HMAC-verified material instead of trusting an unauthenticated header:
- Include the `shop-domain` header (and ideally topic/webhook-id) in the signable string alongside the raw body when validating webhooks, or
- Cross-check that `request.shop` matches a shop value embedded in the signed body/payload before dispatching to handlers, rejecting the request if there's a mismatch.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store (`attacker.myshopify.com`). Shopify sends a genuine webhook, e.g. topic `app/uninstalled`, with a body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture this request (it is a plain HTTPS POST hitting the app's own public webhook endpoint — no interception of Shopify's network required, only observation of a request one legitimately receives).
3. Replay the exact same body `B` and HMAC header to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `HmacValidator.validate` recomputes the HMAC purely over `B` (see `to_signable_string`) and it matches, so `Registry.process` passes validation and invokes the topic handler with `shop: "victim.myshopify.com"` per `lib/shopify_api/webhooks/registry.rb` line 198, causing the app to run victim-tenant logic (e.g., de-registering/deleting the victim's stored session) triggered entirely by attacker-controlled traffic.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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
