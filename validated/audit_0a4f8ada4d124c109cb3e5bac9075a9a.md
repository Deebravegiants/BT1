### Title
Webhook shop-domain header trusted for tenant identification without HMAC coverage - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, and `ShopifyAPI::Webhooks::Registry.process` forwards this value to the app's handler as the tenant identifier, while the HMAC signature that gates webhook processing only ever covers the raw request body.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` simply reads the shop-domain header, unauthenticated: [2](#0-1) 

`Registry.process` validates the HMAC over that signable string and then, without any additional check on `request.shop`, passes it straight to the handler as the tenant/shop identifier: [3](#0-2) 

The identity binding this breaks: `shop header value used as tenant key by the handler` should equal `shop value cryptographically bound to the signed payload`, but the HMAC only binds `raw_body`, not `topic`, `shop-domain`, `webhook-id`, or `api-version`. As a result, once an attacker has *any* validly-signed webhook body+HMAC pair for their own installed shop (which Shopify legitimately issues to every merchant who installs the app, since all shops share one HMAC secret — the app's `client_secret`), the attacker can replay that exact body and HMAC value to the app's webhook endpoint while substituting an arbitrary victim `x-shopify-shop-domain` header. `Utils::HmacValidator.validate` will still pass, because it only recomputes the signature over `@raw_body`: [4](#0-3) 

The gem provides no cross-check that the shop credited with the event is the shop that actually owns the signed content — it hands the untrusted header value to the app's business logic as if it were authenticated.

### Impact Explanation
This crosses a tenant boundary: an app that (reasonably, given the API surface) uses `WebhookMetadata`/`request.shop` as the key to look up sessions, update records, or dispatch tenant-scoped side effects can be made to attribute an attacker's own webhook content to a different, victim merchant's shop — i.e., cross-tenant data injection/corruption using only a webhook that Shopify legitimately signed for the attacker's own store. This matches the "cross-tenant access" Critical impact category, since no part of the identifier that binds the event to a specific merchant is authenticated.

### Likelihood Explanation
Likelihood is high for any app that installs webhooks and trusts `request.shop` (or `WebhookMetadata#shop`) for tenant scoping, which is the documented/expected usage pattern of this API — the gem gives the developer no signal that this field is unauthenticated. The only prerequisite is that the attacker install the target app on a shop they control (a normal, unprivileged action any internet user can take on a public app) in order to obtain a body+HMAC pair signed with the app's shared secret; no leaked credentials, TLS interception, or privileged access is required.

### Recommendation
Include `shop`, `topic`, and `webhook-id` in the HMAC-covered signable string (or otherwise cryptographically bind them, e.g. by validating `shop` against the session/store that the app knows should be receiving this specific webhook subscription) rather than only signing the raw body. At minimum, document prominently that `request.shop` is not authenticated by the HMAC check and must be independently verified against the app's known/installed shop list before being used for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers any webhook topic the app subscribes to (e.g. `orders/create`), causing Shopify to send a POST with a body `B` and a valid `x-shopify-hmac-sha256` header computed as `HMAC-SHA256(app_secret, B)`.
3. Attacker captures `B` and the HMAC value, then replays them to the same webhook endpoint, replacing only `x-shopify-shop-domain: attacker-shop.myshopify.com` with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) only — it passes because `B` and the HMAC are unchanged: [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, letting the attacker inject events attributed to a shop they do not own.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
