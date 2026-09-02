### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating an HMAC that is computed only over the raw request body, while the `shop` (and `topic`, `api_version`, `webhook_id`) values are read directly from HTTP headers that are never included in the signed payload. Any party capable of observing one genuine, validly-signed webhook delivery (e.g. any merchant who installs the same multi-tenant app and receives their own real webhooks) can replay that exact body+HMAC pair while substituting the `x-shopify-shop-domain` header for a different, victim shop, and the app will accept it as an authentic webhook for the victim tenant.

### Finding Description
The identity binding that should hold is:
`hmac == HMAC(secret, bytes_that_determine_the_processed_identity)`

but the implementation only signs the body: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`; `shop`, `topic`, `api_version`, and `webhook_id` are all read from separate, unsigned HTTP headers via `shopify_header`: [3](#0-2) [4](#0-3) 

`Utils::HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string`, so for a `Webhooks::Request` it only ever validates the raw body bytes, never the shop header: [5](#0-4) 

`Registry.process` performs this HMAC check and then immediately trusts `request.shop` to build the metadata passed to the app's webhook handler, with no additional binding between the shop header and the authenticated bytes: [6](#0-5) 

Because every shop installed on a given app shares the same `api_secret_key`, any tenant of a multi-tenant app can legitimately receive a real webhook for their own store, capture the `(raw_body, hmac)` pair (both of which are valid and unrelated to the shop identity), and resend that identical body/HMAC combination to the app's shared webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to a victim shop domain. `HmacValidator.validate` still succeeds because it only checks the raw body against the secret, and `Registry.process` dispatches the handler with `shop: request.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the shop-authenticated-vs-shop-acted-upon binding and grants cross-tenant access: the attacker can cause the app to execute webhook-driven business logic (e.g., order/customer/app-uninstalled handling, data updates, token revocation flows) attributed to a shop they do not control, using only a webhook body they legitimately received for their own installation. This matches the Critical "cross-tenant access" impact category, since the app has no gem-level mechanism to prove the `shop` header is bound to the same request that produced the valid HMAC.

### Likelihood Explanation
Any unprivileged internet user who can install the same app on their own store (a routine, unprivileged action for public/multi-tenant Shopify apps) automatically receives real webhook deliveries with valid HMACs. Replaying that body with a modified shop header requires no secret, no access token, and no privileged access — only a basic HTTP client — making this readily exploitable against any consuming application that relies on `WebhookMetadata#shop` for tenant identification (as the gem's own `Registry.process` does).

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed payload used for HMAC verification, or otherwise cryptographically bind the shop header to the authenticated body before dispatching to handlers — e.g., derive/verify the shop from a source that is itself covered by the HMAC, or maintain a per-shop webhook secret/endpoint rather than relying on a header that sits outside the signed bytes.

### Proof of Concept
1. App merchant A installs the multi-tenant app and Shopify delivers a webhook to the shared endpoint:
   - Headers: `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, `x-shopify-topic: orders/create`
   - Body: `{"id":123,...}`
2. Merchant A (an unprivileged actor w.r.t. other tenants) intercepts this request (they control their own network path/traffic to their own installed app, or the app logs the raw request) and records `raw_body` and `x-shopify-hmac-sha256` verbatim.
3. Merchant A crafts a new POST to the same webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `raw_body` only, which still matches — `Registry.process` in `lib/shopify_api/webhooks/registry.rb` proceeds and invokes the handler with `shop: "victim-shop.myshopify.com"`, causing the application to process attacker-controlled data as if it originated from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/webhooks/request.rb (L66-70)
```ruby

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
