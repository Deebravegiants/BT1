### Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC signature only over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values — which are used by `ShopifyAPI::Webhooks::Registry.process` to select the handler and to identify which merchant the event belongs to — are parsed from HTTP headers that are completely outside the scope of the signature check. An attacker who can obtain any one legitimately HMAC-signed webhook body/signature pair can replay it with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header, and the gem's HMAC validation will still pass.

### Finding Description
`Request#hmac` and `Request#to_signable_string` bind the signature check to `@raw_body` only: [1](#0-0) [2](#0-1) 

```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
```

`Utils::HmacValidator.validate` verifies the signature exclusively against `to_signable_string`, i.e. `@raw_body`: [3](#0-2) 

`Registry.process` then trusts the unauthenticated `shop`, `topic`, `webhook_id`, and `api_version` header values to dispatch and construct `WebhookMetadata` for the app's handler: [4](#0-3) 

The identity binding that should hold is: `bytes verified by HMAC == bytes that determine the tenant (shop) and event type (topic)`. In this implementation, `bytes verified` = `raw_body` only, while `bytes that determine tenant/event` = `shop-domain`/`topic` headers, which are never signed. Because these two sets of bytes are disjoint, the signature check provides no assurance about which shop or topic a given signed body actually belongs to.

### Impact Explanation
Any attacker who has access to one legitimately-signed webhook (trivial to obtain by installing any public app on a free/dev store and letting Shopify deliver a real webhook) can capture the `raw_body` and its valid `X-Shopify-Hmac-SHA256` value, then replay that exact pair to the same app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for an arbitrary victim shop domain (and optionally the `X-Shopify-Topic` header to redirect to a different registered handler). `ShopifyAPI::Webhooks::Registry.process` will accept it because `HmacValidator.validate` only checks the body bytes, and will hand the handler a `WebhookMetadata` claiming the event came from the victim shop. This crosses the tenant boundary the HMAC is supposed to enforce, letting one merchant's traffic be attributed to another merchant inside the host application — a cross-tenant confusion/injection primitive.

### Likelihood Explanation
Likelihood is Medium: no secrets are required, only network access to the app's public webhook endpoint and a legitimately-issued webhook (obtainable for free via a dev store install of any target app). The attacker fully controls which headers accompany the replayed body, since HTTP headers on an inbound request to the app are not otherwise authenticated by this gem.

### Recommendation
Bind the verified identity fields into the signable material, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the signature before trusting them for dispatch — e.g. reject/flag webhooks where the `shop` header does not correspond to a shop with an active, previously-established session/installation record, and avoid relying on unauthenticated headers alone to select handlers or populate `WebhookMetadata`. At minimum, document in `Registry.process`/`WebhookMetadata` that `shop`/`topic` are unauthenticated and must be revalidated by the host app against known installed shops before use.

### Proof of Concept
1. Install any target Shopify app on an attacker-controlled dev store; capture a delivered webhook's raw body `B` and its valid `X-Shopify-Hmac-SHA256` header `H` (computed by Shopify over `B` using the app's shared secret).
2. Send a POST request directly to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Headers: `X-Shopify-Hmac-SHA256: H` (unchanged), `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged), `X-Shopify-Topic: <original topic>`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` (`B`) using the shared secret and finds it matches `H`, since the header spoofing did not alter `B`.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host application to process attacker-supplied data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
