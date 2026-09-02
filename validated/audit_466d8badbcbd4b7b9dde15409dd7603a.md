## Analysis

I searched the OAuth flow (`AuthQuery`) and confirmed `shop` is included in the HMAC-signed string there, so that binding is safe. However, the webhook processing path shows the exact bug class described in the external report: a field that is *acted on* by the code but *not covered* by the HMAC signature. [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body`, while `Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header independently and is never mixed into the signable string. `Registry.process` validates the HMAC only against the raw body, then trusts `request.shop` when constructing `WebhookMetadata` passed to the app's handler: [2](#0-1) [3](#0-2) 

### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header not covered by HMAC — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from only the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` attribute is parsed directly from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header without being included in the signed payload. `Registry.process` validates the HMAC against the body only and then forwards the unauthenticated `shop` value to the app's `WebhookHandler` via `WebhookMetadata`. This breaks the intended identity binding: `hmac_valid(body) == true` is treated as proof that `shop == <the shop the body actually originated from>`, but the gem never enforces `shop ∈ signed(body)`.

### Finding Description
Shopify's webhook authenticity model is supposed to guarantee that a request with a valid HMAC originated from Shopify for a specific installed shop. In this gem's implementation, the equality that should hold is:
`valid_hmac(raw_body, secret) ⇒ shop_header == originating_shop`

But because `to_signable_string` only ever returns `@raw_body` [4](#0-3) , and the `shop` accessor is read from a separate, unsigned header [5](#0-4) , that equality is never enforced by this gem. `Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching `request.shop` to the handler [2](#0-1) .

Since any shop that installs the app can capture a legitimately-signed webhook delivery (body + valid HMAC) for its own store — e.g., by inspecting outgoing requests to their own callback endpoint — that attacker-controlled shop can replay the identical `(raw_body, hmac)` pair directly to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value. The HMAC check still passes because it validates only the body against the shared `api_secret_key`, which the attacker never needs to know. The handler then receives `data.shop` set to any value the attacker chooses, even though the actual authenticated party (the body's real author) was a different shop.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an app that uses `data.shop` from the webhook handler to attribute/store data per-merchant (a normal pattern shown in the gem's own docs, `data.shop` is documented as "The shop domain of the webhook") can be made to associate attacker-supplied webhook body content with an arbitrary victim shop identifier. Depending on how the host app trusts this field (e.g., to look up per-shop credentials, write records, or trigger per-shop side effects), this enables cross-tenant data injection/corruption without needing any of the victim's credentials.

### Likelihood Explanation
Medium-to-high. Any merchant who installs the app is, by definition, capable of receiving genuinely-signed webhook deliveries for their own shop and can capture and replay them to the app's public HTTP callback endpoint with a modified shop header. No secret key or privileged access is required — only having installed the app once and access to standard HTTP tooling.

### Recommendation
Bind the shop domain into the HMAC-verified payload rather than trusting an independent header. For example, include the `shop-domain` header value (and other identity-relevant headers such as `topic`/`webhook-id`) in `to_signable_string`, or otherwise cross-check `request.shop` against a shop value obtained from a source that is itself covered by the signature (mirroring how `AuthQuery#to_signable_string` already binds `shop` into its signed string, see `lib/shopify_api/auth/oauth/auth_query.rb`). At minimum, document prominently that `data.shop` in `WebhookMetadata` is unauthenticated and must not be trusted for tenant attribution without independent verification (e.g., checking it corresponds to a shop with an active, stored session/installation).

### Proof of Concept
1. App-owning attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Shopify delivers a legitimately HMAC-signed webhook to the app's callback endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and some JSON body.
3. Attacker captures this exact `(raw_body, hmac)` pair (e.g., via browser devtools/network capture on their own infrastructure, or a proxy in front of their own endpoint).
4. Attacker sends a new POST request directly to the app's public webhook callback path, reusing the identical body and `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes the HMAC over `@raw_body` [4](#0-3) .
6. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, even though the payload actually originated from the attacker's shop [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
