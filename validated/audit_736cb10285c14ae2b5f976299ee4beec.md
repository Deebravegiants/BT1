### Title
Webhook shop identity spoofing via HMAC scope gap (topic/shop/api_version/webhook_id not authenticated) - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop`, `topic`, `api_version`, and `webhook_id` values taken from unauthenticated HTTP headers to build the `WebhookMetadata` passed to the app's handler. Because the HMAC signable string is only the JSON body, the shop attribution of a webhook is not cryptographically bound to the signature that authenticates it.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic tie to the signature: [2](#0-1) 

`Registry.process` validates only that the body's HMAC matches, then immediately trusts `request.shop`/`request.topic`/etc. to construct the metadata delivered to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` (used identically for both OAuth callbacks and webhooks) computes the signature purely over `verifiable_query.to_signable_string`: [4](#0-3) 

The binding that should hold is: `shop_header == shop_that_produced_the_signed_body`. Because the signature covers only body bytes, this equality is never checked — the HMAC is valid for *any* headers as long as the body bytes are unchanged. A single `api_secret_key` is shared across every shop that has installed a given app (Shopify signs webhooks per-app, not per-shop), so any actor who can obtain one genuine signed webhook delivery for the app (e.g., by installing the app on their own store — an unprivileged action requiring no credentials from the target) possesses a body+HMAC pair that remains valid when replayed with an arbitrary `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) header pointing at a victim shop. `Registry.process` will accept it as valid and hand `WebhookMetadata` with the attacker-chosen `shop` to the app's handler, which typically uses `shop` to select which merchant's data/session the payload applies to.

### Impact Explanation
This breaks the tenant-identity binding the app relies on to decide *which merchant* a webhook event belongs to, enabling cross-tenant data confusion/injection: an attacker can make the app believe an event (with attacker-controlled or replayed body content) originated from a different, victim shop. Depending on how the consuming app trusts `WebhookMetadata#shop` (e.g., to look up a session/access token or write data keyed by shop), this can lead to cross-tenant state corruption or triggering actions against a different merchant's stored data — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Moderate: the attacker needs one authentic signed webhook body for the target app (trivial to obtain by installing the app on their own store, which requires no privileged credentials), plus the ability to POST to the app's public webhook endpoint with custom headers (also trivial, since webhook endpoints are internet-facing by design). No `api_secret_key`, access token, or victim credentials are needed.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed payload verification, or otherwise cryptographically bind them (e.g., require the `shop` returned by `Registry.process` to be corroborated against a `mac`-covered value or a known/registered shop record before dispatching to the handler), rather than trusting header values as soon as body-only HMAC validation succeeds.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, generating a genuine webhook delivery: body `B`, headers including `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays a request to the app's webhook endpoint with the exact same body `B` and HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally forges `x-shopify-topic`/`x-shopify-webhook-id` to steer to a different handler).
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` succeeds because it only re-computes the HMAC over `raw_body`, which is unchanged. [5](#0-4) 
4. `Registry.process` proceeds to call the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, even though `victim.myshopify.com` never produced this event. [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
