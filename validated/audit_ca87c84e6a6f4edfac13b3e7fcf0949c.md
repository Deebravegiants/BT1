### Title
Webhook shop-tenant identity not covered by HMAC allows cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw request body, while the `shop` (tenant identifier) is read from a separate, unauthenticated HTTP header. Any actor who can obtain one genuinely-signed webhook delivery (trivially available to anyone who installs the app on their own store) can replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header for a victim shop, and the gem's verification logic will accept it as authentic for the victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` is derived purely from the `hmac-sha256` header: [1](#0-0) 

`Request#shop` is read independently from the `shop-domain` header, with no relationship to the signed bytes: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then dispatches to the handler using the unauthenticated `request.shop` value: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` value taken from the same untrusted header set: [4](#0-3) 

The identity binding that should hold is:
`shop_header_used_for_tenant_dispatch == shop_that_Shopify_actually_signed_the_payload_for`

Because the `shop-domain` header is excluded from `to_signable_string`, this equality is never checked. An attacker who legitimately installs the app on their own shop receives a genuinely HMAC-signed webhook (body + `hmac-sha256` header valid for the api_secret_key they don't even need to know). They can capture that exact `(raw_body, hmac)` pair and re-POST it to the app's public webhook endpoint with the `shop-domain` header changed to any victim shop. `HmacValidator.validate` still passes because it never touched the header, and `Registry.process` forwards `shop: request.shop` (the forged victim shop) together with the attacker's own body/topic to the app's `WebhookHandler`.

### Impact Explanation
This crosses a tenant boundary: an app's webhook handler (which apps typically use to key data by `shop`) can be made to process attacker-controlled webhook content (topic + JSON body) as if it originated from a different merchant's store, without any credential belonging to that victim. Depending on the handler, this enables cross-tenant data injection/corruption (e.g., fake `orders/create`, `app/uninstalled`, `customers/redact` events attributed to the victim shop), which falls under "cross-tenant access."

### Likelihood Explanation
Any internet user can install the target app on a shop they control (free/dev store) and thereby obtain a validly-signed webhook without needing the app's `api_secret_key`, an access token, or any privileged account. Sending an HTTP POST to the app's public webhook callback with a modified header is trivial and requires no TLS interception or special access — only knowledge of the app's public webhook URL, which is inherently public.

### Recommendation
Bind the tenant identifier into the signed material, or otherwise cryptographically tie `shop-domain` to the payload before trusting it for dispatch. At minimum, `Registry.process`/`Request` should cross-check that the `shop-domain` header is consistent with a value derivable from the signed body (e.g., verify against the shop stored for the corresponding `webhook_id`/subscription, or include shop in the HMAC computation as Shopify's newer verification schemes do), rejecting the webhook if there's a mismatch — mirroring the recommended fix in the referenced report of checking that the two identifiers ("address" and "id", here "shop header" and "signed payload origin") actually correspond before acting.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a shop they control) and triggers a webhook (e.g., `orders/create`).
2. Shopify sends: `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid-signature-over-body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and a JSON body describing the attacker's own order.
3. Attacker captures this exact request (they control the receiving traffic in their own environment/proxy) and re-issues an HTTP POST directly to the app's public webhook endpoint, keeping the body and `X-Shopify-Hmac-Sha256` header identical, but replacing `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `@raw_body` only and it matches — validation succeeds.
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...))`, causing the app to process attacker-supplied data as belonging to the victim shop's tenant.

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
