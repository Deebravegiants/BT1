### Title
Webhook shop/topic identity headers are not covered by the HMAC signature, allowing tenant-spoofed webhook delivery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `Registry.process` trusts the unauthenticated `shop-domain` (and `topic`/`webhook_id`/`api_version`) headers as the tenant identity handed to the app's webhook handler. The HMAC check therefore verifies "the bytes are an authentic webhook payload signed with the app secret" but the code then acts on a different, unverified value (`request.shop`) for tenant attribution — the exact class of bug in the H-24 report: a check performed on one quantity while a materially different, uncovered quantity is what downstream logic actually relies on.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
only the `@raw_body` is signed. The `shop`, `topic`, `webhook_id`, and `api_version` accessors all come straight from HTTP headers that are never part of the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the HMAC strictly over `to_signable_string` (i.e., the body): [3](#0-2) 

`Webhooks::Registry.process` performs this HMAC check and, immediately after it passes, forwards the **unauthenticated** `request.shop` value into `WebhookMetadata` that is handed to the app's handler as the tenant identifier: [4](#0-3) 

Equality the check actually proves: `HMAC(secret, body) == received_hmac`.
Equality the code implicitly assumes and acts on: `shop_header == "the shop that generated this body"`.
These are not the same statement — `shop_header` can be swapped for any value by anyone able to produce one valid `(body, hmac)` pair, since the header isn't part of the signed material.

### Impact Explanation
Any unprivileged user who can trigger one legitimate webhook delivery to an app they control (e.g., install the app on their own development/test shop and cause an event such as `orders/create`) obtains a valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key` (shared across all installs of the app, not per-tenant). They can then replay that exact body/HMAC to the app's single shared webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. Because `Registry.process` never re-derives or cross-checks `shop` against anything covered by the HMAC, the host application's handler executes believing the event belongs to the victim tenant — a cross-tenant data/action confusion. This matches the "Critical - cross-tenant access" impact category, and requires no `api_secret_key`, access token, or privileged account — only ordinary app-installation capability available to any internet user.

### Likelihood Explanation
Likelihood is high for any host application that uses `WebhookMetadata#shop` (or `request.shop`) as the sole tenant key when persisting or acting on webhook data — a common integration pattern documented for this gem's webhook handler interface. No secret material needs to be recovered; only one genuine webhook delivery needs to be observed/triggered by the attacker.

### Recommendation
Do not trust `shop`/`topic`/`webhook_id`/`api_version` headers unless they are cryptographically bound to the request. Either include these header values in the HMAC-signed string used by `to_signable_string`, or, at minimum, have `Registry.process`/`WebhookMetadata` validate the `shop` header against a shop that is known to be entitled to receive webhooks for this app (e.g., cross-check against installed-shop records) before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers an `orders/create` event, capturing the legitimate webhook `raw_body` and `x-shopify-hmac-sha256` header sent by Shopify (signed with the app's `api_secret_key`).
2. Attacker POSTs the exact same `raw_body` + `x-shopify-hmac-sha256` to the app's shared webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC: [5](#0-4) 
4. `Registry.process` builds `WebhookMetadata` with `shop: request.shop` = `"victim-shop.myshopify.com"` and invokes the handler, which now processes attacker-controlled data attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
