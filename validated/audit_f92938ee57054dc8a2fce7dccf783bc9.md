### Title
Webhook Requests Trust an Unauthenticated `shop`/`topic` Header Not Covered by the HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the shop identity (`x-shopify-shop-domain`), the event topic, and the webhook id are all read straight from unauthenticated HTTP headers and never bound into that signature. Because a single app-wide `api_secret_key` is shared across every tenant, anyone who can obtain one valid `(body, hmac)` pair for their own shop (any merchant can install a public app or use a free/dev store) can replay that same body and hmac against the app's webhook endpoint while substituting the `shop` header to point at a different, victim tenant. `Utils::HmacValidator.validate` will accept it, and the handler will process attacker-controlled data as if it came from the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from HTTP headers with no cryptographic protection: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then unconditionally trusts the header-derived `shop`/`topic`/`webhook_id` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` verifies only `verifiable_query.hmac == HMAC(api_secret_key, verifiable_query.to_signable_string)`, i.e. `HMAC(secret, raw_body)`: [4](#0-3) 

Because `api_secret_key` is a single per-app secret shared across every shop that installs the app (not per-tenant), a valid `(raw_body, hmac)` pair computed for tenant A's webhook event is equally "valid" for any other tenant B, since the shop identity is never part of the signed material. The binding that should hold — `shop claimed in header == shop whose event actually produced this signed body` — is never checked; only `hmac == HMAC(secret, body)` is checked, independent of `shop`.

### Impact Explanation
This allows cross-tenant webhook forgery/impersonation: an unprivileged installer of the app (any merchant able to install a public app or spin up a low-cost/dev store) can capture one genuine `(body, hmac)` pair delivered to their own store, then send a forged HTTP request directly to the app's public webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header rewritten to target another merchant's shop. The application's webhook handler will process this as authentic data for the victim shop (e.g. triggering order/customer/app-uninstalled processing, GDPR data-request handling, billing events, etc., depending on what topics the app subscribes to), impersonating events for a shop the attacker does not control. This meets the Critical "cross-tenant access" impact bar since the tenant boundary (`shop`) is not covered by the only integrity check performed.

### Likelihood Explanation
Likelihood is moderate-to-high: obtaining one legitimate `(body, hmac)` pair requires nothing more than installing the target app on any Shopify store (including a free development store) and triggering a subscribed webhook topic — this is available to any internet user, not a privileged account. No knowledge of `api_secret_key` or any merchant's access token is required. The only constraint is that the forged webhook must reuse a body that was legitimately signed (so payload content is somewhat constrained), but topic/shop headers are fully attacker-controlled, which is often sufficient to trigger destructive handler logic (e.g. re-triggering `app/uninstalled` or `customers/redact` against an arbitrary shop).

### Recommendation
Bind the tenant/topic identity into the authenticated material instead of trusting bare headers:
- Include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (Shopify does not sign these itself, so the app must additionally validate that the claimed `shop` is one that is actually registered/installed for this app instance, e.g. by checking it against stored session/install records before dispatching to a handler).
- At minimum, document/enforce that consumers of `WebhookMetadata#shop` must independently verify the shop is a known, currently-installed tenant before trusting webhook-derived data, since the HMAC alone does not authenticate the shop claim.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` (any user can do this for a public app or via a Shopify dev/partner store).
2. Attacker triggers a webhook topic the app subscribes to (e.g., updates an order), and captures the raw request the app receives, including the body and the `x-shopify-hmac-sha256` value Shopify computed, e.g.:
```
POST /webhooks
x-shopify-topic: orders/updated
x-shopify-shop-domain: attacker-shop.myshopify.com
x-shopify-hmac-sha256: <valid-hmac-of-body>
x-shopify-webhook-id: ...

{ "id": 123, ... }
```
3. Attacker resends the exact same body and `x-shopify-hmac-sha256` value directly to the app's public webhook endpoint, but changes:
```
x-shopify-shop-domain: victim-shop.myshopify.com
```
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `lib/shopify_api/webhooks/registry.rb` line 190 passes because it only checks `HMAC(api_secret_key, raw_body)`, which is unchanged. `Registry.process` then invokes the registered handler with `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-controlled data as an authentic event from the victim tenant.

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
