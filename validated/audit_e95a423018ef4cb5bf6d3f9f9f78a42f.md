### Title
Webhook HMAC does not bind the `shop-domain` header, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body. The `shop` value that is subsequently handed to the app's webhook handler — and that a host application uses to attribute the payload to a specific merchant/tenant — is read directly from the `X-Shopify-Shop-Domain` header, which is never included in the signed material. Anyone who can obtain one valid `(raw_body, hmac)` pair for the shared app secret (trivially available by installing the app on their own store, since the same `api_secret_key` signs every shop's webhooks) can replay that pair to the app's single shared webhook endpoint while substituting an arbitrary `shop-domain` header, causing the host app to process attacker-controlled data as if it originated from a victim shop.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes and compares the HMAC using `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [2](#0-1) 

But `shop` (and `topic`, `webhook_id`, `api_version`) are parsed straight from unauthenticated headers: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches to the registered handler using `request.shop`, which was never covered by the signature: [4](#0-3) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop value acted upon by the handler`

Because the HMAC only binds `raw_body`, this equality does not hold: an attacker can keep `raw_body`/`hmac` fixed (both valid, since they were legitimately produced for the attacker's own installed shop, signed with the app's single shared `api_secret_key`) and change only the `shop-domain` header to any victim `myshopify.com` domain. `Registry.process` still calls `Utils::HmacValidator.validate(request)` successfully (body is unchanged) and then invokes the handler with `shop: <attacker-chosen victim domain>`.

### Impact Explanation
Host applications are documented to key persistent state (installation status, tokens, orders, customer data ingestion, uninstall handling, GDPR mandatory webhooks, etc.) by the `shop` field delivered in `WebhookMetadata`, exactly as shown in the library's own docs (`ShopifyAPI::Webhooks::Registry.process` example). Since `shop` is not authenticated, an attacker can inject arbitrary webhook payloads (e.g., spoofed `orders/create`, `app/uninstalled`, `customers/data_request`) attributed to any victim shop domain, causing cross-tenant data corruption/spoofing in the host application — a Critical-level cross-tenant access impact per the scope of this exercise.

### Likelihood Explanation
The attacker only needs to be an unprivileged internet user who can install the target app on their own (attacker-owned) shop — a normal, unprivileged self-service action requiring no leaked credentials, access tokens, or `client_secret`. Because every shop's webhooks are signed with the same app-wide `api_secret_key` and delivered to the same shared endpoint URL, a valid `(raw_body, hmac)` pair obtained from the attacker's own shop's traffic remains valid when replayed with a forged `shop-domain` header. No TLS interception or privileged access is required — only observing traffic the attacker's own installation legitimately receives.

### Recommendation
Include the shop identity in the material that is verified, or otherwise cryptographically/contextually bind the header value that is trusted:
- Extend `Request#to_signable_string` (or `HmacValidator`) to incorporate `shop-domain` (and ideally `topic`) into the signed payload check, or
- Require/verify that `shop` corresponds to a shop actually known/installed by the host app (this can be documented as a mandatory step) before handing `WebhookMetadata` to handlers, and update `docs/usage/webhooks.md`'s example, which currently implies the raw HMAC check alone is sufficient authentication of `data.shop`.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker-shop.myshopify.com`; register a webhook topic (e.g., `orders/create`).
2. Capture a genuine webhook delivery to the app's shared endpoint: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)`).
3. Replay a request to the same endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which only checks `B` against `H` — passes.
5. Handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled data is processed under the victim's tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
