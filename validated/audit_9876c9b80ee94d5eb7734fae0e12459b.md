### Title
Webhook shop/topic/webhook_id identity headers are not covered by the HMAC, allowing cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers and are never part of the signed payload. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally passes these unauthenticated header values to the application's handler as trusted identity data, despite the gem's own documentation claiming that `process` "will verify the request did indeed come from Shopify."

### Finding Description
The signable content for a webhook request is defined as: [1](#0-0) 

Only `@raw_body` is signed. The `shop`, `topic`, `webhook_id`, and `api_version` accessors read straight from headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC over the body, then forwards the unauthenticated headers (`request.shop`, `request.topic`, `request.webhook_id`, `request.api_version`) directly into `WebhookMetadata` for the app's handler: [3](#0-2) 

The identity binding broken here is: `hmac-verified bytes (raw_body)` ≠ `bytes the handler treats as authenticated (shop header, topic header, webhook_id header)`. Because Shopify's webhook signing scheme (which this gem replicates) HMACs only the body, any actor capable of obtaining one genuine `(raw_body, hmac)` pair — e.g., a merchant who installs the app on their own store and receives real webhooks for it — can replay that same body/hmac pair to the app's public webhook endpoint while substituting arbitrary values for `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id`. `HmacValidator.validate` will still pass because it only checks the body: [4](#0-3) 

The docs reinforce that this check is meant to establish provenance of the whole request, not just the body: [5](#0-4) 

### Impact Explanation
An app that uses `data.shop` (per the documented handler contract) to look up or act on a specific merchant's session/store record can be made to process attacker-controlled body content under a victim shop's identity, or vice versa — genuine data from shop A can be relabeled as belonging to shop B. This is a cross-tenant confusion primitive: the handler's notion of "which shop this event is for" is not bound to the cryptographically verified content, letting one tenant (the attacker's own shop) inject events that are attributed to another tenant purely by forging headers.

### Likelihood Explanation
Exploitation requires only that the attacker control one shop with the app installed (an ordinary, unprivileged merchant account) to obtain one legitimate `(raw_body, hmac)` pair, and the ability to send arbitrary HTTP headers to the app's public webhook endpoint — both trivially available to any user who can install the app. No access to `api_secret_key`, tokens, or the app's infrastructure is required.

### Recommendation
Bind the identity headers into the signed payload check, or otherwise cryptographically/authoritatively verify `shop`, `topic`, and `webhook_id` against Shopify (e.g., cross-check against the registered webhook subscription for that topic/shop, or require the app to independently verify the shop is one that actually has the app installed and match it against session storage) before trusting these values in `WebhookMetadata`. At minimum, update the documentation to clarify that HMAC validation only authenticates the body, not the shop/topic/webhook_id headers, so host applications know they must independently validate shop identity.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Shopify sends a legitimate webhook request to the app with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
3. Attacker captures this `(raw_body, hmac)` pair.
4. Attacker replays a new HTTP POST to the same webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or a different `x-shopify-topic`.
5. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers, `HmacValidator.validate` succeeds because it only checks `raw_body` against the same secret-derived HMAC, and `Registry.process` invokes the handler with `data.shop == "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own store.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
