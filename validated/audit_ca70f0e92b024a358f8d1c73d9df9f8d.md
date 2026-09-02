## Title
Webhook Shop-Tenant Confusion via HMAC Coverage Gap — Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The gem's webhook verification computes the HMAC over the raw request body only, while the `shop` (tenant identity) is taken from an HTTP header that is never included in the signed material. Because a single app-level `api_secret_key` is shared across every shop that has installed the app, any party who can obtain one validly-signed webhook delivery (e.g. by installing the app on their own store) can replay that exact `body`+`hmac` pair while substituting the `shop-domain` header for a victim shop, and the gem will report the request as authentic for the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read straight from an unauthenticated header, entirely outside the signed data: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string` — for `Request` that is the body alone, so `shop` never participates in the equality check that HMAC is meant to enforce: [3](#0-2) 

`Registry.process` accepts the request the moment `HmacValidator.validate` succeeds, then forwards `request.shop` — the unauthenticated header value — directly to the application's webhook handler as the tenant identity for the event: [4](#0-3) 

The broken identity binding, stated as an equality the gem should enforce but does not:
`HMAC(secret, signed_bytes) == received_hmac` is checked, but `signed_bytes` excludes `shop`, so the gem effectively verifies `shop_claimed_by_attacker == shop_delivered_to_handler` with no cryptographic tie to `shop_that_actually_owns_this_hmac`. Since the `api_secret_key` is shared by every shop that installs the same app, a valid `(body, hmac)` pair obtained from *any* installation (including one the attacker legitimately controls) remains valid when replayed with an arbitrary `shop-domain` header naming a different, victim tenant.

### Impact Explanation
This breaks the app's tenant boundary: an attacker who has installed the target app on a shop they control can capture one genuine webhook delivery and replay it toward the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop, letting the attacker inject fabricated events (e.g. `orders/create`, `app/uninstalled`, GDPR/customer webhooks) into another merchant's data pipeline — a cross-tenant access/data-injection primitive, which the rules classify as Critical.

### Likelihood Explanation
Requires only: (1) normal, unprivileged ability to install the app on an attacker-controlled shop to obtain one legitimate `(body, hmac)` sample, and (2) sending an HTTP request to the app's public webhook endpoint with a forged `shop-domain`/`x-shopify-shop-domain` header. No access token, `client_secret`, or leaked credential of the victim is needed — only the shared app secret's signature, which the attacker obtains passively via their own legitimate installation.

### Recommendation
Bind `shop` to the signed material or to an out-of-band trusted source before dispatching to handlers:
- Include the `shop-domain` header (and ideally `topic`, `webhook-id`) in the HMAC-signed string, or
- Require the host application to cross-check `request.shop` against the shop associated with the currently active/stored session/subscription for that `webhook_id`/topic before invoking the handler, and document this requirement prominently, or
- Have `Registry.process` reject requests where the delivered `shop` cannot be correlated with a known, previously-registered subscription for that shop.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (normal, unprivileged flow) and configures a webhook subscription, e.g. `orders/create`.
2. Shopify delivers a legitimate webhook to the app's endpoint:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over body>`.
   - Body: `{"id": 1, ...}`.
3. Attacker captures `body` and `x-shopify-hmac-sha256` verbatim, then resends the same request to the app's public webhook endpoint but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (the unchanged body) and finds it matches — validation passes.
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the host application to process/store fabricated data as if it originated from the victim tenant.

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
