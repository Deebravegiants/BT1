### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw HTTP body only. The `shop-domain` header — which the library hands to application webhook handlers as the tenant identifier — is never included in the signed data. An attacker who can produce one valid `(body, hmac)` pair (e.g. by installing the app on their own store and triggering a webhook) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header, and `HmacValidator` will still accept it as authentic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from an unauthenticated header with no cross-check against the signed content: [2](#0-1) 

`Registry.process` validates the HMAC and then passes `request.shop` straight to the application handler as the tenant/shop identity, with no additional binding check: [3](#0-2) 

`HmacValidator.validate` only verifies `HMAC(secret, verifiable_query.to_signable_string) == hmac`, i.e. it authenticates the **body**, never the **shop**: [4](#0-3) 

The equality that should hold is: `shop attributed to the processed webhook == shop that the HMAC was actually computed for`. Because `to_signable_string` excludes the `shop-domain` header, this equality is never enforced — the HMAC only binds the body, so any shop-domain value can be attached to a validly-signed body.

### Impact Explanation
Since the app's `client_secret` is shared across all merchants that install the app, and the webhook HMAC is computed over the body only, an attacker who legitimately installs the app on their own store (an unprivileged action requiring no special credentials) can obtain a body+HMAC pair that is valid under the app's secret. They can then send that identical body and HMAC directly to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a victim shop. `Registry.process` will accept it as authentic and dispatch it to the app's handler tagged with the victim's shop, because nothing in the gem binds the HMAC to the shop identity. This is a cross-tenant identity bypass: data intended to be scoped to shop A can be injected and processed as if it belongs to shop B, potentially corrupting per-tenant state, or being used to trigger the app to make Shopify API calls against victim shop's session/data with attacker-controlled payload content.

### Likelihood Explanation
Any user who can install (or use a free/dev install of) the app on a shop they control can generate a legitimate webhook delivery and observe its raw body and HMAC (via their own webhook receiver logs, request capture, or by using a public request-bin as the webhook target if permitted, or by directly crafting/replaying the request to the target app's public endpoint). No access to the app's `client_secret`, access tokens, or any privileged account belonging to the victim is required — only the ability to trigger one webhook for a shop the attacker legitimately controls and knowledge of the target app's public webhook URL.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) in the HMAC-signed material, or otherwise cryptographically bind the verified body to the claimed shop before dispatching to handlers — e.g., require the shop domain to be validated against Shopify's known/expected format via `Utils::ShopValidator` AND cross-checked against the merchant's stored session/webhook registration record (topic+webhook_id+shop tuple) rather than trusting the header at face value once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged install).
2. Attacker triggers a webhook (e.g. `orders/create`) with body content they fully control (their own order data). Shopify computes `hmac = HMAC-SHA256(client_secret, raw_body)` and POSTs to the app's webhook endpoint with headers:
   - `X-Shopify-Hmac-Sha256: <hmac>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - `X-Shopify-Topic: orders/create`
3. Attacker captures `raw_body` and `hmac` (they own the receiving log/capture for their own webhook).
4. Attacker sends a new POST directly to the app's public webhook endpoint with the identical `raw_body` and `hmac`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the body against the HMAC; `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches the handler with `shop: "victim-shop.myshopify.com"`, even though this payload was never actually sent by Shopify for that shop.

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
