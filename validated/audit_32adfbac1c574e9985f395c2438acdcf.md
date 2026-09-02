### Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements the `Utils::VerifiableQuery` interface but signs only the raw HTTP body via `to_signable_string`, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` trusts these header-derived fields to route and label the payload passed to the app's handler, even though `Utils::HmacValidator.validate` never verifies them.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers with no cryptographic binding to the signed bytes: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` header value — it never incorporates `shop`, `topic`, or the other header fields into the signed message: [3](#0-2) 

`Registry.process` validates only this body HMAC, then dispatches the handler using `request.shop` and `request.topic` taken directly from the (unverified) headers: [4](#0-3) 

This is the same class of bug as the reported `RewardPool.burn()`/`move()` issue: two logically distinct operations (or, here, two distinct identity/action fields) share one signature scheme, but the scheme fails to bind all the fields that are actually acted upon. The equality that should hold is:
`bytes_verified_by_hmac == bytes_that_determine_the_acted_upon_tenant_and_action`
Here that equality is broken: `bytes_verified_by_hmac = raw_body` only, while `bytes_that_determine_the_acted_upon_tenant_and_action = raw_body + shop-domain + topic + webhook-id + api-version` (all header-derived, attacker-controlled, unauthenticated).

### Impact Explanation
Because the shop-domain (tenant identity) is not part of the signed message, an attacker who is able to obtain any single legitimate `(raw_body, hmac)` pair — e.g., from a real webhook Shopify sends to their own store for an app they control, which requires no privileged access to the victim's tenant — can replay that exact body/HMAC pair to the target app's webhook endpoint while forging the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, and `X-Shopify-Api-Version` headers to claim a different (victim) shop. `Utils::HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` will invoke the merchant's webhook handler with `WebhookMetadata` that misattributes the payload to a shop the attacker does not own. Any app logic that trusts `request.shop`/`data.shop` to index or act on tenant data (a common and endorsed pattern per this gem's own webhook API) can be tricked into writing/associating attacker-supplied data under another merchant's identity — a cross-tenant integrity issue.

### Likelihood Explanation
Exploitation requires only the ability to receive one legitimate webhook from Shopify to any store the attacker controls (trivial for anyone with a free/dev Shopify store and the target app installed on it) and the ability to send arbitrary HTTP requests with forged headers to the target app's public webhook endpoint. No `api_secret_key`, access token, or privileged account for the victim tenant is needed, matching the "unprivileged internet user" threat model.

### Recommendation
Include the identity/action-determining fields in the signed message so the signature is scoped to the specific shop/topic/webhook, not just the body. Concretely, either:
- Bind `shop`, `topic`, `webhook_id`, and `api_version` into `to_signable_string` (e.g., canonicalize and concatenate them with the body before HMAC comparison), mirroring Shopify's actual webhook verification guidance of validating the full raw request in the context of the expected shop, or
- At minimum, require host apps/document that `request.shop` must be cross-checked against a known/expected shop for that endpoint/session before trusting it, and treat `HmacValidator.validate` success as proof only of body integrity, not of the header-derived routing fields.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app registers (e.g. `orders/create`) so Shopify sends a legitimately-signed webhook: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's real secret).
2. Capture `B` and `H` off the wire (attacker's own traffic to their own endpoint — no privileged access needed).
3. Replay to the same app's public webhook endpoint with:
   - `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Body: `B` (unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, `X-Shopify-Api-Version` forged as desired.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds, per [5](#0-4) .
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)`, per [6](#0-5) , causing the app to process attacker-supplied payload data attributed to the victim shop.

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
