## Title
Webhook `shop`, `topic`, and `webhook_id` are not covered by the HMAC signature, allowing tenant/topic spoofing on replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` fields are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` uses the HMAC check as proof that the *entire* webhook (including which shop it came from) is genuine, but the signature never actually covers the shop identity. This breaks the identity binding: `shop authenticated == shop used to route/attribute the webhook`.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from headers, none of which are part of the signed content: [2](#0-1) 

`HmacValidator.validate` only compares `verifiable_query.hmac` against a signature computed over `to_signable_string` (the raw body) — headers are never part of the check: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to trust `request.shop` and `request.topic` for dispatching to the handler: [4](#0-3) 

Because the signature is computed over the body only, any request with a *valid (body, hmac) pair for some shop* — for example a webhook the attacker legitimately receives for their own installed app/shop, or any webhook body an attacker can otherwise get Shopify to sign — remains fully valid after the attacker swaps the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers to arbitrary values. `HmacValidator.validate` still returns `true` since it never inspects those headers, and `Registry.process` will hand the (attacker-chosen) `shop` and `topic` to the app's handler as if they were verified.

This is the direct analog of the reported bug class: a field ("shop"/"topic", acting like the session/tenant key) is *acted upon* by the code but is not covered by the cryptographic check ("HMAC") that is supposed to authenticate the whole message — equivalent to "shop authenticated ≠ shop used as session key."

### Impact Explanation
An attacker who can obtain even one genuine `(raw_body, hmac)` pair (e.g., by installing the app on their own store and capturing a real webhook Shopify sends them) can replay that exact body/HMAC to the app's webhook endpoint while forging the `shop-domain` and `topic` headers to point at a different shop/topic. Since `Registry.process` passes `request.shop` unchanged into `WebhookMetadata` for the handler, any app logic that uses `data.shop` to look up per-tenant records, sessions, or to gate/attribute the processed body will act on the wrong tenant — a cross-tenant data/action confusion. Depending on what the host app's webhook handler does with `shop` (e.g. writing data keyed by shop, dispatching admin API calls using that shop's stored session), this can result in cross-tenant access or corruption of another merchant's data.

### Likelihood Explanation
Exploitation requires only a single valid `(body, hmac)` pair, which any developer/attacker can trivially obtain for their own shop by installing the app and receiving one real webhook (a normal, unprivileged action) — no access token, `client_secret`, or privileged account is needed. Forging the remaining plaintext headers is trivial once the attacker controls the HTTP request being sent to the app's webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable content (or otherwise cryptographically bind them, e.g. by deriving the shop solely from a value that Shopify includes as authenticated context rather than a bare header), so that `HmacValidator.validate` fails if any of these header values are altered relative to what Shopify actually signed.

### Proof of Concept
1. App owner (attacker) installs the target app on `attacker-shop.myshopify.com` and triggers an action that causes Shopify to send a real webhook — attacker captures `raw_body B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the shared secret).
2. Attacker resends the request to the same webhook endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and/or a different `X-Shopify-Topic`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` parses successfully; `HmacValidator.validate(request)` returns `true` because it only recomputes HMAC over `B`.
4. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker's own body content, despite Shopify never having signed this shop/topic combination.

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
