### Title
Webhook shop-domain and topic headers are trusted for tenant routing while only the raw body is HMAC-covered - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating that the HMAC covers the raw request body, then unconditionally trusts the `shop-domain` and `topic` headers—neither of which is included in the signed payload—to route the event and identify the tenant.

### Finding Description
The bug-class hint (a value used to make a security decision that is not actually bound by the accompanying integrity check) maps directly onto this gem's webhook verification path.

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/verifies the HMAC purely over that signable string using `Context.api_secret_key`: [2](#0-1) 

But `Request#shop`, `#topic`, and `#webhook_id` are simply read from HTTP headers with no cryptographic binding to the signed body: [3](#0-2) 

`Registry.process` then uses exactly these unauthenticated header values to look up the handler and to construct the `WebhookMetadata` that is handed to the app's handler as the identity of the store and event: [4](#0-3) 

The equality the gem should be enforcing is:
`shop_bound_by_signature == shop_used_for_tenant_routing`

but what it actually enforces is only:
`hmac(raw_body, secret) == received_hmac`,
with `shop` (and `topic`) carried out-of-band in headers that are never mixed into the signable string.

Because the signature only binds the body, a party who has received one genuine, validly-signed webhook for their own shop (any merchant can install the app and receive webhooks addressed to their own store — no privileged token or secret required) can replay that same raw body + HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` value. `Utils::HmacValidator.validate` will still pass, because it only checks that the body matches the HMAC, not that the body "belongs" to the claimed shop. `Registry.process` will then dispatch to the handler with `WebhookMetadata#shop` set to the attacker-chosen value, causing the host application (which relies on this gem's documented `Registry.process`/`WebhookMetadata` API to determine the tenant) to attribute/apply the payload to a different, arbitrary shop.

### Impact Explanation
This breaks the shop-identity binding that webhook consumers rely on to know which tenant a payload belongs to, enabling cross-tenant data injection/confusion: a webhook body genuinely signed for shop A can be replayed and attributed to victim shop B purely by changing an unauthenticated header. This matches the "cross-tenant access" Critical-impact category, since it is the gem's own `Registry.process` implementation (not host-application misuse) that trusts the unauthenticated header for tenant identity.

### Likelihood Explanation
Likelihood is high for an unprivileged actor: no access token, `client_secret`, or privileged account is needed. An attacker only needs to be able to install/uninstall the app on their own store (or otherwise obtain one genuinely-signed webhook body/HMAC pair for a known event) and can then submit forged HTTP requests directly to the app's webhook endpoint with a spoofed `shop-domain` header, exploiting the exact code path in `Registry.process`.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the signed material that is verified, or otherwise cross-check them against a value that is authenticated—for example, incorporate the `shop-domain` header into `to_signable_string`, or require the host app to independently confirm the header-derived shop against a known, previously-provisioned shop record before trusting `WebhookMetadata#shop`. At minimum, document prominently that `request.shop`/`request.topic` are not integrity-protected by the HMAC and must not be used as the sole tenant identifier.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) to capture a genuine `raw_body` and its valid `x-shopify-hmac-sha256` value (both computed with the real `client_secret`, but observable by the attacker since they are delivered to the attacker's own endpoint).
2. Replay the captured request to the app's webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` unchanged, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because `to_signable_string` only inspects `raw_body`: [5](#0-4) 
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-controlled `shop` header value and invokes the handler as if the event came from `victim.myshopify.com`: [4](#0-3)

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
