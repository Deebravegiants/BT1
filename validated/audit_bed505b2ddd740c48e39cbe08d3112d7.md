### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for a given shop as long as `Utils::HmacValidator.validate(request)` succeeds. However, the HMAC is computed only over the raw request body — the `shop` value (`x-shopify-shop-domain` header) that is dispatched to the app's `WebhookHandler` as the tenant identifier is never included in the signed material. This breaks the identity binding `hmac(secret, signed_bytes) == hmac(secret, "trusted binding of body AND shop")`; instead the gem verifies `hmac(secret, body) == hmac(secret, body)` while independently trusting an unauthenticated `shop` field for tenant attribution — the same class of bug as the flash-loan report, where a trusted party (`onlyLendingPool`) was verified but the untrusted field actually acted upon (`_initiator`) was not checked against it.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from an attacker-controllable HTTP header with no cross-check against the signed bytes: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e., the raw body) against the computed HMAC — it never binds `shop`: [3](#0-2) 

`Registry.process` accepts the request purely based on that body-only HMAC check, then forwards the untrusted `request.shop` to the handler as the trusted tenant identifier: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` with no further verification, and is explicitly documented as "The shop domain of the webhook" for hosting apps to key their tenant lookups on: [5](#0-4) [6](#0-5) 

**Attack path**: A user who owns a legitimate (unprivileged) shop that has the app installed will receive a genuine Shopify webhook signed with `HMAC-SHA256(app.client_secret, raw_body)`. Since all shops share the same app-level `client_secret` for HMAC signing (this is a single, app-wide key, not shop-specific), and the `shop` header is not part of the signed bytes, the attacker can capture one legitimately-signed `(raw_body, hmac)` pair from their own shop, then replay it directly to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still returns `true` (it only checks the body/hmac pair), so `Registry.process` calls the handler with `WebhookMetadata#shop` set to the victim's domain while the body content actually belongs to the attacker's own shop.

### Impact Explanation
Any host application that follows the gem's documented pattern of using `data.shop` to select/attribute per-tenant state (session lookup, data writes, job dispatch as shown in the gem's own docs example `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be made to process attacker-supplied webhook content under a victim shop's identity. This is a cross-tenant identity-binding failure directly analogous to the flash-loan initiator bug: a signature check on one field (body/lending-pool caller) is substituted for a check that should also bind another field actually acted upon (shop/initiator).

### Likelihood Explanation
Requires only an unprivileged internet user who can install the app on their own shop (obtaining one legitimately-signed webhook body/hmac pair) and can send an arbitrary HTTP POST to the app's public webhook receiving endpoint — no access to `api_secret_key`, tokens, or privileged accounts is needed.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind `shop` to the verified payload before it is handed to `WebhookHandler#handle`, e.g., by having `Registry.process` cross-check `request.shop` against a shop value embedded in (or derivable only from) the HMAC-covered body, rather than trusting the header value independently of the signature.

### Proof of Concept
1. Attacker installs the app on shop `attacker.myshopify.com` and receives a legitimate webhook POST with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for the app's shared `client_secret`).
2. Attacker sends a new POST to the app's public webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) computes the HMAC over `B` only and returns `true`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `WebhookMetadata.shop == "victim.myshopify.com"` and `body` from the attacker's own webhook, causing the host app to process attacker data under the victim's tenant identity.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
