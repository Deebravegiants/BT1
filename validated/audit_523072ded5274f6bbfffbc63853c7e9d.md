### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb), [lib/shopify_api/webhooks/registry.rb](lib/shopify_api/webhooks/registry.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature verified by `Utils::HmacValidator.validate` never covers the `shop-domain` header. `Registry.process` nonetheless forwards `request.shop` to the host application's handler as the trusted tenant identifier. Because an app's webhook signing secret (`Context.api_secret_key`) is a single value shared across every merchant installation, anyone who can obtain one validly-signed webhook body (e.g., by installing the app on their own store) can replay it directly to the app's webhook endpoint with an arbitrary `shop-domain` header and have it accepted as coming from a different, victim shop.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, body || shop)`, i.e. the "shop" the handler trusts should equal the shop the HMAC actually authenticates. Instead:

- `Request#to_signable_string` signs only `@raw_body`: [1](#0-0) 
- `shop` is read straight from an attacker-controlled header with no cryptographic binding: [2](#0-1) 
- `Registry.process` checks the HMAC (over the body only) and then hands `request.shop` to the handler as if it were verified: [3](#0-2) 
- The HMAC secret is a single, app-wide secret (`Context.api_secret_key`), not per-shop, so any shop's legitimately signed webhook body/HMAC pair remains valid regardless of which `shop-domain` header accompanies it: [4](#0-3) 

Because webhook endpoints are ordinary HTTP endpoints reachable by anyone on the internet (Shopify's delivery is not the only path to them), an attacker who has installed the target app on their own store receives real webhooks with valid `X-Shopify-Hmac-Sha256` values for their own body content. They can then POST that same body/HMAC pair to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` with any other merchant's `*.myshopify.com` domain. `HmacValidator.validate` still succeeds (it never looked at the shop header), and `WebhookMetadata` is built with `shop: request.shop` pointing at the victim shop, so the host application processes attacker-supplied data (e.g., `orders/create`, `app/uninstalled`, GDPR topics) under the wrong tenant's identity.

### Impact Explanation
This breaks the shop-authentication boundary between tenants: the gem hands the host application a `shop` value it presents as verified, but it is not bound to the HMAC that was actually checked. Any host app that keys persistence, entitlements, or side effects (e.g., app-uninstall cleanup, order fulfillment records, GDPR erasure) off `WebhookMetadata#shop` can be made to apply attacker-chosen data to an arbitrary victim shop's tenant — a cross-tenant access/data-integrity violation, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Medium-to-high: no privileged credentials, session, or `api_secret_key` are required. The only precondition is the attacker being able to install the target app on some shop they control (a normal, unprivileged action for public/embedded Shopify apps) to obtain one valid signed webhook, and knowledge that the endpoint is reachable directly over HTTP outside Shopify's delivery infrastructure.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signable string used for webhook HMAC verification, mirroring how `AuthQuery#to_signable_string` incorporates `shop`, `host`, etc. Concretely, change `Request#to_signable_string` to include a canonical representation combining the raw body with the `shop-domain` header (this requires coordinating with Shopify's webhook signing scheme, or alternatively cross-checking `request.shop` against a shop known to be associated with the currently active session/store before invoking the handler) rather than trusting the header as an authenticated value on its own.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, triggering a webhook, e.g. `orders/create`, which Shopify delivers with headers:
   - `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - `X-Shopify-Hmac-Sha256: <valid HMAC over raw_body using the app's single api_secret_key>`
   - `raw_body: {"id": 1, ...}`
2. Attacker captures this request and replays it directly to the app's public webhook endpoint, but replaces the header:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - keeps the same `raw_body` and `X-Shopify-Hmac-Sha256` (still valid, since the signature never depended on the shop header).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the shared app secret (`lib/shopify_api/utils/hmac_validator.rb:12-22`).
4. `Registry.process` builds `WebhookMetadata.new(shop: request.shop, ...)` with `shop == "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), and the host app's handler processes attacker-controlled order data as if it belonged to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
