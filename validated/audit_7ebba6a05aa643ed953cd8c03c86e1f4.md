Confirmed: the vulnerability is in `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`.

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing via header substitution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` authenticates an inbound webhook solely by validating an HMAC computed over the raw HTTP body, yet the `shop` (and `topic`, `webhook_id`, `api_version`) values that are subsequently trusted and handed to the app's webhook handler are read directly from unauthenticated HTTP headers, which are not part of the signed material.

### Finding Description
`Webhooks::Registry.process` authenticates a webhook exclusively via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field of the query object: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns **only** `@raw_body` — the raw JSON body of the webhook — while `hmac` is parsed from the `hmac-sha256` header. Critically, `shop`, `topic`, `webhook_id`, and `api_version` are all derived from separate HTTP headers that are never included in the signed string: [3](#0-2) 

After HMAC validation succeeds (which only proves the body bytes are authentic, i.e., signed with `api_secret_key`), the registry builds `WebhookMetadata` directly from these unauthenticated header-derived fields and dispatches it to the app's handler as the identity of the webhook's owning shop: [1](#0-0) 

This breaks the intended binding: `hmac_valid(body) == true` is treated as equivalent to `shop == owning_tenant_of(body)`, but `shop` is never cryptographically bound to `body`. Any party capable of obtaining one valid `(raw_body, hmac)` pair — for instance, a merchant who installs the app and legitimately receives a genuine webhook for their own store — can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to name a different, victim shop. `HmacValidator.validate` still succeeds because it only checks `raw_body`, and `Registry.process` will happily dispatch the replayed payload labeled as belonging to the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding failure: an attacker with no privileged access to the victim's data can cause the app's webhook handler to process attacker-controlled payload/topic combinations attributed to an arbitrary shop of the attacker's choosing. Depending on what the host application's webhook handlers do with `WebhookMetadata#shop` (e.g., writing to per-shop records, triggering per-shop side effects, invalidating/deleting per-shop data, or driving business logic keyed by `shop`), this enables cross-tenant data corruption or unauthorized actions performed against a shop the attacker does not own — matching the "cross-tenant access" high/critical impact class. This directly mirrors the reported bug class: a value that is acted upon (the shop identity) is not covered by the integrity check (the HMAC) that is meant to guarantee it is trustworthy.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple shops: any user who can become a legitimate installer of the app (a normal, unprivileged action — installing a free/public app requires no special privilege) automatically receives real webhooks with valid `(body, hmac)` pairs for their own shop, which is all that's needed to mount the attack against any other shop by simply resending the request with a modified `shop-domain` header. No access token, `client_secret`, or knowledge of `api_secret_key` is required — only a body/HMAC pair the attacker legitimately received.

### Recommendation
Include the `shop` domain (and ideally `topic`) in the HMAC-signed material for webhook requests, or otherwise separately verify that the `shop` header value matches an installation known to the app *before* trusting it, rather than relying solely on the un-bound header. Since Shopify's own HMAC scheme for webhooks signs only the body (per Shopify's webhook spec), the library should, at minimum, document this gap prominently and/or provide a hook so host apps can bind `shop`/`topic` against their own trusted state (e.g., verifying the shop exists in `Registry`'s registered topics-to-shop mapping, or requiring TLS + comparing against the session store) rather than the current design where `Registry.process` unconditionally trusts header-derived `shop`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (a normal, unprivileged install action).
2. Shopify sends the attacker's app instance a legitimate webhook, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"id": 1, "note": "malicious-payload"}
   ```
3. Attacker captures this exact `body` and `x-shopify-hmac-sha256` value.
4. Attacker resends the identical body and HMAC header to the app's public webhook endpoint, but replaces the shop header:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same-valid-hmac-of-body>
   x-shopify-shop-domain: victim.myshopify.com
   Body: {"id": 1, "note": "malicious-payload"}
   ```
5. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `@raw_body`, which is unchanged.
6. `Webhooks::Registry.process` in `lib/shopify_api/webhooks/registry.rb` builds `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: ..., ...)` and invokes the app's handler as if this data genuinely originated from `victim.myshopify.com`, even though it never involved that shop.

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
