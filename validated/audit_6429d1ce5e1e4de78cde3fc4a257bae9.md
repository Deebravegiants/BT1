### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted despite not being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The reported bug class is a Certifier interface whose `getData` is never bound to real data, so callers trust a value that was never actually verified. The direct analog in this gem is `ShopifyAPI::Webhooks::Request`: the HMAC signature that `Utils::HmacValidator` validates is computed over the raw request body only, while the `shop`, `topic`, and `webhook_id` headers that `Webhooks::Registry.process` uses to build the trusted `WebhookMetadata` passed to the app's handler are read straight from unauthenticated HTTP headers and never included in the signed bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `#hmac` is read from the `hmac-sha256` header: [1](#0-0) 

`Utils::HmacValidator.validate` verifies the HMAC strictly against `verifiable_query.to_signable_string`, i.e. the body only: [2](#0-1) 

`Request#shop`, `#topic`, and `#webhook_id` are parsed directly from the `shop-domain`, `topic`, and `webhook-id` headers, with no cryptographic binding to the signature at all: [3](#0-2) 

`Webhooks::Registry.process` validates only the body HMAC, then forwards `request.shop`, `request.topic`, and `request.webhook_id` verbatim into `WebhookMetadata`, which is handed to the app's webhook handler as trusted identity data: [4](#0-3) [5](#0-4) 

The broken identity binding, expressed as an equality that should hold but doesn't:
`hmac_signed_bytes(request) == body` while `trusted_identity_used_by_handler(request) == {shop, topic, webhook_id} ⊄ hmac_signed_bytes(request)`.

Because the app's global `client_secret` (used to compute the webhook HMAC) is shared across every shop that installs the app, any unprivileged internet user who operates their own Shopify store, receives one legitimately signed webhook body (with a valid HMAC), can then resend that exact `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` (and/or `topic`/`webhook_id`) header of their choosing. `HmacValidator.validate` still passes (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-chosen) `shop` and `topic`, with data that actually originated from the attacker's own shop.

### Impact Explanation
If the host application's webhook handler uses `data.shop` (from `WebhookMetadata`) as the tenant key for writing to its own data store — which is exactly the pattern the gem's own webhook docs/`WebhookHandler` interface encourage — an attacker can inject data attributed to a victim shop, or overwrite/trigger tenant-scoped side effects (e.g. mandatory `customers/redact`, `shop/redact` topics) against a shop they do not own. This is cross-tenant data confusion/injection achieved without any of the app's credentials, satisfying the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own legitimate, installed shop (freely obtainable, a normal unprivileged Shopify merchant/developer account), (2) triggering any webhook event on that shop to capture a valid `(body, hmac)` pair, and (3) replaying it to the app's public webhook endpoint with a forged `shop-domain`/`topic` header. No secret material, TLS interception, or privileged access is needed — likelihood is high wherever a consuming app trusts `WebhookMetadata#shop`/`#topic` as an authenticated tenant identifier, which is the documented intended use of the field.

### Recommendation
- Do not treat `Request#shop`, `#topic`, or `#webhook_id` as authenticated merely because the body HMAC validated. At minimum, document prominently (and ideally enforce in `Registry.process`) that the `shop` header must be cross-checked against an existing installed/offline session for that shop before any tenant-scoped action is taken.
- Where feasible, bind the header values into the signable payload check (e.g., require callers to pass the expected shop/topic and assert equality against the header-derived values before calling `handler.handle`), or clearly document that `shop`/`topic` headers are not covered by the signature and must be independently authorized by the app.
- Reject webhook requests whose `topic` does not match the topic looked up via `@registry[request.topic]` combined with an explicit registered-shop check, rather than trusting the header value directly for dispatch and metadata.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` (a normal, unprivileged action any developer can perform).
2. Attacker triggers any subscribed webhook topic (e.g. `orders/create`) on their own shop, capturing the raw POST body `B` and the resulting `X-Shopify-Hmac-SHA256` header `H` sent by Shopify (computed as `HMAC-SHA256(client_secret, B)`).
3. Attacker replays a request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it only covers `B`)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - Header `X-Shopify-Topic`: chosen freely, e.g. `customers/redact` (forged)
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(client_secret, B) == H` — this succeeds. [6](#0-5) 
5. The app's registered handler for that topic is invoked with `WebhookMetadata.new(topic: "customers/redact", shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)`, causing tenant-scoped logic to run against the victim shop's identity with attacker-supplied data.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
