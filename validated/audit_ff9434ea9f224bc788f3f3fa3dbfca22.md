### Title
Webhook `shop-domain` header is trusted for tenant identity but not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header that is **not included** in the HMAC-signed payload, while `ShopifyAPI::Webhooks::Registry.process` uses that same unauthenticated header to attribute the webhook body to a shop before dispatching it to the app's handler. This breaks the identity binding: `shop authenticated (by HMAC) != shop used to process the event`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

`ShopifyAPI::Webhooks::Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic relationship to the HMAC signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC exclusively over `verifiable_query.to_signable_string` (the raw body), and never touches header values such as `shop`, `topic`, or `webhook-id`: [3](#0-2) 

`Registry.process` validates only this body-only HMAC, then dispatches the event using the unauthenticated `request.shop` value as the tenant identifier passed to the app's own webhook handler: [4](#0-3) 

Because the `api_secret_key` used to compute the HMAC is the *app's* single secret (not a per-shop secret), any shop that has legitimately installed the app can obtain a validly-signed `(raw_body, hmac)` pair for its own webhook deliveries (e.g. by triggering an `orders/create` event on its own store, or replaying an old Shopify delivery). Since the `shop-domain` header sits entirely outside the signed content, this unprivileged attacker (a legitimate multi-tenant user of the same app) can resend the identical body/HMAC pair while substituting the `shop-domain` header for any victim shop that also uses the app. `HmacValidator.validate` still returns `true` because the body is untouched, and `Registry.process` will invoke the app's handler with `WebhookMetadata` claiming the forged shop, `shop: request.shop`, feeding attacker-controlled data into the victim tenant's webhook processing pipeline.

This is the same bug class as the reported `Bribe.sol` issue: a tracked/trusted value (`totalVoting` / `shop`) is updated or acted upon along one path (`deposit` / webhook dispatch) without being protected/verified consistently with the other bound value (`withdraw`'s missing decrement / the HMAC signature), breaking the intended invariant `signed content == trusted identity`.

### Impact Explanation
This allows cross-tenant access: an attacker who is merely another (potentially free/dev) installer of the same public app can forge webhook events that the app attributes to any other shop using the app, without needing that victim's credentials, access token, or the app's `client_secret`. Depending on how the host application's webhook handlers use `shop` (e.g. looking up/updating that shop's stored data, triggering side effects tied to the shop record), this can lead to cross-tenant data corruption or disclosure purely through this gem's own trust boundary — the exact "shop authenticated versus shop stored/used as key" identity-binding failure called out as in-scope.

### Likelihood Explanation
Likelihood is realistic: the attacker only needs their own legitimate app installation (trivial to obtain for public apps, e.g. a free developer store) to generate a validly HMAC-signed body, then a single crafted HTTP request to the app's webhook endpoint with a swapped `shop-domain` header. No secrets, tokens, or privileged access to the victim shop are required.

### Recommendation
Bind the shop identity to the signed content — either include the shop domain (and other identifying headers used to route the event) inside the HMAC-signed material, or require the host application to independently verify that `request.shop` corresponds to a shop with a currently valid, stored access token/session before trusting the webhook payload. At minimum, document/require an explicit shop-authorization check in `Registry.process` before invoking `handler.handle`.

### Proof of Concept
1. Attacker installs the target public app on their own shop `attacker.myshopify.com` and triggers any webhook (e.g. `orders/create`), capturing the raw request body `B` and header `shopify-hmac-sha256: H` that Shopify sent (`H` is `HMAC-SHA256(api_secret_key, B)`).
2. Attacker resends an HTTP POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `shopify-hmac-sha256`: `H` (unchanged)
   - Header `shopify-shop-domain`: `victim-shop.myshopify.com` (changed)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and finds it equal to `H` — validation passes because the domain header was never part of the signed string: [5](#0-4) 
4. The handler is invoked with `shop: "victim-shop.myshopify.com"` and attacker-controlled body content, even though Shopify never sent this event for that shop: [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
```
