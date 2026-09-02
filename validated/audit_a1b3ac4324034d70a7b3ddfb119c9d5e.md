## Title
Webhook `shop` header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for a given shop as soon as `Utils::HmacValidator.validate(request)` succeeds, then hands `request.shop` straight to the app's handler. However the HMAC is computed only over the raw body, while `shop` is read from an HTTP header that is completely outside the signed content. Anyone who can obtain one valid `(body, hmac)` pair for their own installation can replay it against the app's webhook endpoint with an arbitrary `shop-domain` header, making the app process the payload as if it belonged to a different (victim) merchant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which plays no part in that signable string: [2](#0-1) 

`HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string` (the body) and compares it with `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` gates everything on this single HMAC check and then forwards the unauthenticated `request.shop` value directly into the handler's metadata: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop delivered to the handler`. Because `shop` is a plain header outside the signed bytes, that equality is never enforced — the gem authenticates the *bytes* but attributes them to whatever `shop-domain` header the caller supplies.

### Impact Explanation
An attacker who installs the target app on their own store (a normal, unprivileged action available to anyone) receives genuine webhooks with a valid `hmac-sha256` for a given body. They can then POST that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting the `shop-domain` header with any victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), so `Registry.process` calls the handler with `WebhookMetadata.new(shop: request.shop, body: request.parsed_body, ...)` where `shop` is the attacker-chosen victim domain and `body` is attacker-controlled content that was never sent by that shop. This is a cross-tenant integrity breach: the app is made to believe and act on data as if it came from a shop it did not come from, e.g. writing/overwriting per-shop records, changing per-shop state, or triggering shop-scoped side effects for a merchant the attacker does not control.

### Likelihood Explanation
Likelihood is realistic: obtaining a valid `(body, hmac)` pair requires nothing more than installing the app once on any shop (including an attacker's own free/dev store) and capturing one webhook delivery, which is standard, unprivileged interaction with the app. No access to `api_secret_key`, tokens, or any Shopify-internal credential is needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`api-version`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the verified body (e.g., include the shop domain in the signable string, or independently verify that the shop the app expects for this webhook subscription matches the header before trusting it). At minimum, `Webhooks::Request#shop` should not be treated as authenticated output when only the body was covered by the HMAC.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives a real webhook:
   - headers: `shopify-shop-domain: attacker.myshopify.com`, `shopify-hmac-sha256: <valid hmac for body B>`
   - body: `B`
2. Attacker replays the same request to the app's webhook endpoint, only changing the header:
   - headers: `shopify-shop-domain: victim.myshopify.com`, `shopify-hmac-sha256: <same valid hmac for body B>`
   - body: `B` (unchanged)
3. `Utils::HmacValidator.validate` recomputes HMAC over body `B` with the app's `api_secret_key` and it matches (the secret and body are the same as step 1), so validation passes.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data attributed to a shop the attacker never installed on.

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
