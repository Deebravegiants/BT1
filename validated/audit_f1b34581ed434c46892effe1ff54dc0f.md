### Title
Webhook shop-domain identity spoofing via HMAC that only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body. The `shop` (and `topic`/`webhook_id`) values that the handler subsequently trusts and acts upon are read from separate, unauthenticated HTTP headers that are never included in the signed material. Any caller who can obtain one valid `(raw_body, hmac)` pair — for example a merchant who legitimately installed the app and received a real webhook for their own shop — can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` header, and the app's webhook handler will process the payload as if it originated from a victim shop of the attacker's choosing.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read from headers that are completely outside that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC only against `verifiable_query.to_signable_string` (i.e., the body), never the shop header: [3](#0-2) 

`Webhooks::Registry.process` performs exactly this HMAC check and then immediately trusts `request.shop` to construct the metadata handed to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop_value_verified_by_hmac == shop_value_delivered_to_handler`

In this implementation the left-hand side does not exist at all — the HMAC binds nothing about the shop — so the equality trivially fails: an attacker can keep the right-hand side (`request.shop`) under their control while satisfying the HMAC check with any previously-observed valid `(body, hmac)` pair, regardless of which shop that pair was originally generated for.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: `Registry.process` passes the attacker-chosen `shop` straight into `WebhookMetadata` given to the host application's handler: [5](#0-4) 

Any handler that keys business logic, database writes, or entitlement checks off `data.shop` (the documented, intended use of this field) can be made to act on behalf of a shop the attacker does not own, using a body/HMAC pair the attacker legitimately obtained for their own tenant. This is a cross-tenant identity-binding bypass carried through the gem's own webhook-authentication API.

### Likelihood Explanation
Reaching this requires only:
1. Being (or becoming) any merchant who installs the app and registers for a webhook topic — an unprivileged action.
2. Capturing one delivered `(raw_body, X-Shopify-Hmac-Sha256)` pair for their own shop.
3. Replaying it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to the victim shop.

No access token, `client_secret`, or `api_secret_key` is needed by the attacker — they consume the gem's exposed `Registry.process`/`Request` API exactly as documented, so the flaw is fully reachable through this gem's own code path.

### Recommendation
Include the shop domain (and topic/webhook id, if they are relied upon) in the HMAC-signed material, or otherwise cryptographically bind the header-derived identity fields to the payload before trusting them. At minimum, `Webhooks::Registry.process`/`Request` should not expose an unauthenticated `shop` value to handlers as though it had been verified by `HmacValidator.validate`; document/require host apps to independently corroborate `shop` against a known, previously-authenticated identifier (e.g., an installed-shop record) rather than trusting the header value implied to be "verified" by the preceding HMAC check.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook, capturing the raw body `B` and header `X-Shopify-Hmac-Sha256: H` (a valid HMAC of `B` under the app's `api_secret_key`, which the attacker never needs to know).
2. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - `X-Shopify-Topic`: same or different registered topic
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H`, so validation succeeds.
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process data/logic under the identity of `victim-shop.myshopify.com` despite the request never being authenticated for that shop.

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
