### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the HMAC of an incoming webhook, then passes `request.shop` (taken from the `x-shopify-shop-domain` HTTP header) to the app's `WebhookHandler`. The HMAC is computed only over the raw request body, so the `shop` header is a completely unauthenticated value with respect to the signature check.

### Finding Description
`Utils::HmacValidator.validate` is invoked in `Registry.process`: [1](#0-0) 

The signature is verified against `Request#to_signable_string`, which returns only the raw body: [2](#0-1) 

But `Request#shop` is read straight from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header, entirely outside the signed content: [3](#0-2) 

`Registry.process` then forwards this unauthenticated `shop` value straight into the `WebhookMetadata` struct handed to the app's handler: [4](#0-3) [5](#0-4) 

The identity equality that should hold is: `shop bound by HMAC == shop acted on by the handler`. Here, the HMAC only proves "this body was signed with the app's `api_secret_key`" — it says nothing about which shop the header claims to be from. Since the `api_secret_key` is a single app-wide secret shared across every shop that installs the app, any shop that legitimately installs the app receives genuinely-signed webhook deliveries. An attacker who installs the app on their own shop can capture one of these validly-signed webhook payloads (the raw body/HMAC pair) and replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` because it only checks the (unchanged) raw body against the (unchanged) HMAC, and `Registry.process` will call the handler with `shop:` set to the victim's domain.

### Impact Explanation
This breaks the shop/tenant identity binding that host applications rely on to route webhook data to the correct merchant's records. A host app that uses `data.shop` from `WebhookMetadata` to select which tenant's data to create/update/delete (the intended and expected way to use this metadata) can be made to write attacker-controlled webhook data into a different merchant's account, or trigger merchant-scoped side effects (e.g., app-managed billing, inventory sync, order processing) attributed to a shop the attacker doesn't own. This is a cross-tenant data integrity issue reachable by any unprivileged internet user who is able to install the app on any single shop (including a free/trial shop they control) and then send a modified HTTP request to the app's public webhook endpoint — no access token, `api_secret_key`, or privileged account for the victim shop is required.

### Likelihood Explanation
Likelihood is high for any app that both processes webhooks and derives tenant-selection logic from `WebhookMetadata#shop` as delivered by this gem (which is the gem's documented usage pattern — see `docs/usage/webhooks.md`'s `ShopifyAPI::Webhooks::Registry.process` example). All an attacker needs is: (1) install the target app on any shop they control (trivial, free), (2) capture one genuine webhook delivery (raw body + `X-Shopify-Hmac-Sha256`), (3) replay it with a forged `X-Shopify-Shop-Domain` header pointed at the victim shop. The `HmacValidator` performs no binding check between the header-derived `shop` and the signed content, so this passes validation unconditionally.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values in the signable content that is HMAC-verified, or otherwise cryptographically bind the shop domain to the request before it's trusted by `WebhookMetadata`. At minimum, the gem should document prominently that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the host app against a known/installed shop list before being used to select tenant data — but a documentation caveat alone doesn't remove the exploit path through the gem's own trust boundary (`Registry.process` treats a validated `HmacValidator.validate` as an all-clear to hand off `request.shop` unchallenged).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, receiving the app's shared `api_secret_key`-signed webhooks legitimately (e.g., `orders/create`).
2. Attacker captures one such webhook HTTP request: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's `api_secret_key`), per [6](#0-5) .
3. Attacker POSTs to the app's webhook endpoint with the same body `B` and HMAC header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (`= B`) and confirms it matches `H` — validation succeeds, per [7](#0-6) .
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, per [4](#0-3) .
6. Any host app logic keyed on `data.shop` for tenant selection now operates on the victim shop using attacker-supplied webhook content.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
