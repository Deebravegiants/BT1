### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook data injection via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, and then hands the handler a `WebhookMetadata` object built from `request.shop`, `request.topic`, `request.webhook_id`, and `request.parsed_body` [1](#0-0) . However, the HMAC is only computed over the raw request body (`to_signable_string` returns `@raw_body`), never over the `shop-domain`, `topic`, `webhook-id` or `api-version` headers [2](#0-1) . This is structurally identical to the reported bug class: "a field acted on but not covered by the HMAC" — here, the `shop` value used to attribute webhook data to a tenant is disjoint from the bytes actually verified by the signature.

### Finding Description
`Request#hmac` and `Request#to_signable_string` prove that only `@raw_body` is signed: [3](#0-2) 

`Request#shop`, `#topic`, and `#webhook_id` are read from unauthenticated headers with no cryptographic binding to the body or the HMAC: [4](#0-3) 

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop` as the tenant identity forwarded to the app's handler: [1](#0-0) 

Because `shop` is excluded from the signed bytes, the equality the gem implicitly promises to the host application — `hmac_verified(body) == true` implies `shop header == the shop that produced this body` — does not hold. An attacker who can obtain one legitimately-signed webhook body+HMAC pair (e.g., as the owner/operator of any shop that installs the app — a completely unprivileged position, not requiring any of the app's secrets) can resend that exact `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still pass (it only checks the body against the secret), and the handler will receive `WebhookMetadata` claiming the payload belongs to a victim shop it never came from.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce: data cryptographically proven to originate from Shop A can be relabeled and injected into Shop B's processing pipeline purely by an unprivileged party replaying a webhook they legitimately received for their own shop. Any host application that (reasonably, per the gem's documented API) uses `WebhookMetadata#shop` as the authoritative tenant key for updating records, queues, or business logic is exposed to cross-tenant data corruption/injection. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The prerequisite is low: the attacker only needs to be a merchant who has installed the app (thus is sent normal signed webhooks for their own store) and can replay an HTTP request with a modified header — no access to `api_secret_key`, access tokens, or any other credential is required, and no host-application misuse is needed since the gem's own `process` method performs the only validation and exposes the unauthenticated header value as trusted metadata.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) header value into the HMAC-covered material, or otherwise cryptographically tie the accepted `shop` to the specific signed payload (e.g., include it in the signable string, or require the caller to independently verify the shop against a known/installed-shop allowlist before trusting `WebhookMetadata#shop`). At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant-identity source without additional verification.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com`:
   - Headers: `x-shopify-hmac-sha256: <valid HMAC of BODY>`, `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`
   - Body: `BODY` (order JSON for shop A)
2. Attacker (who is the operator of `shop-a.myshopify.com`, an unprivileged merchant) captures this exact request.
3. Attacker resends the identical `BODY` and identical `x-shopify-hmac-sha256` value to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `shop-b.myshopify.com` (a different, victim tenant of the same app).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `BODY` against `api_secret_key` [5](#0-4) .
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: <shop A's order data>, ...)` [6](#0-5) , causing shop A's data to be processed under shop B's tenant context.

### Citations

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
