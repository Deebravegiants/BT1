### Title
Webhook shop/topic/webhook-id headers are trusted without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `topic`, `shop`, `webhook_id`, and `api_version` values used to route and attribute the webhook are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then trusts these header-derived values to select the handler and to populate `WebhookMetadata`, breaking the binding `hmac-authenticated content == content attributed to shop/topic`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#topic`, `Request#shop`, `Request#webhook_id`, and `Request#api_version` are all read straight from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`HmacValidator.validate` (invoked via `VerifiableQuery`) checks only `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. the body, never the headers: [3](#0-2) 

`Registry.process` performs the HMAC check and then immediately trusts the header-derived `topic` and `shop` to pick the handler and construct the metadata object handed to application code: [4](#0-3) 

Because `shop`, `topic`, and `webhook_id` are outside the HMAC's coverage, any party capable of capturing one genuinely-signed `(body, hmac)` pair delivered by Shopify (e.g. a merchant triggering a webhook for their own store and observing the request sent to the app's public webhook endpoint) can replay that exact `(body, hmac)` pair while substituting arbitrary values for `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id`. The signature check still succeeds because it only re-hashes the untouched body, yet the handler and `WebhookMetadata.shop`/`WebhookMetadata.topic` now reflect attacker-chosen, unauthenticated values.

### Impact Explanation
This breaks the identity binding "the shop/topic the HMAC-authenticated payload came from" versus "the shop/topic the app attributes and acts on," which is squarely the class of bug called out in the rules ("a field acted on but not covered by the HMAC"). Any host application that uses `WebhookMetadata#shop` to select a tenant/session (a documented, expected usage pattern, e.g. via `SessionRepository` look-ups keyed by shop) can be made to process a replayed, attacker-obtained payload under a different shop's identity, or dispatch it to a handler for a different topic than the one Shopify actually fired — a cross-tenant confusion condition.

### Likelihood Explanation
The attacker needs to obtain one valid `(body, hmac)` pair for any topic on their own store — trivial for any merchant using the app, since Shopify delivers such webhooks routinely and the merchant/attacker can observe the exact bytes sent to the app's public webhook endpoint (it's just an HTTP POST to their own configured URL). No access to `api_secret_key` or any privileged credential is required; only header manipulation on a replayed request is needed to change the attributed shop/topic.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed material (or otherwise cryptographically bind them to the body before verification), and/or have `Registry.process` cross-validate the `shop` header against the actual owning shop of the webhook subscription rather than trusting it outright. Short term, document/emphasize that host apps must independently verify `shop`/`topic` are consistent with the expected registration before using them for tenant routing.

### Proof of Concept
1. App registers an HTTP webhook handler for topic `orders/create` keyed by `shop`.
2. Attacker (a legitimate merchant of the app) creates an order in their own store `attacker-shop.myshopify.com`, causing Shopify to POST a validly HMAC-signed webhook to the app's public webhook URL:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`
   - Body: `{...order json...}`
3. Attacker captures this exact `(body, hmac)` pair (e.g. by controlling the receiving endpoint temporarily, or via any network visibility they have into their own webhook traffic).
4. Attacker replays the same body and HMAC to the app's endpoint again, but with header `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body: [5](#0-4) 
6. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", ...)`, and any app logic keyed on `shop` now operates under the wrong tenant's identity: [6](#0-5)

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
