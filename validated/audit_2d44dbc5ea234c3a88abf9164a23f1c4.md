## Title
Webhook `shop` (and other identifying headers) are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop` (and `topic`/`webhook_id`/`api_version`) header values to the app's handler as trusted tenant identity — but those header values are never included in the HMAC signature.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` as returning only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers instead, and are never mixed into the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` — i.e. it only proves the body bytes are unmodified, not that any header is bound to that body: [3](#0-2) 

`Registry.process` treats HMAC success as full authentication of the request and forwards `request.shop` straight to the app's webhook handler as the tenant identifier, with no separate check that this shop is the one the body/HMAC actually belongs to: [4](#0-3) 

This differs from the OAuth callback path, where `AuthQuery#to_signable_string` explicitly includes `shop` in the signed parameters, so a callback's `shop` claim is cryptographically bound to the HMAC: [5](#0-4) 

No equivalent binding exists for webhooks. The identity equality the gem should enforce — `shop_bound_by_hmac == shop_used_for_tenant_routing` — does not hold for webhook processing, because `shop` is outside the signed byte range entirely.

### Impact Explanation
An unprivileged attacker who can obtain any single valid `(raw_body, hmac)` pair sent to the app's public webhook endpoint (e.g. from a webhook their own shop legitimately received, from logs, from a network capture, or from a topic that reveals another merchant's data) can replay that exact body/HMAC while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Webhook-Id`/`X-Shopify-Topic`/`X-Shopify-Api-Version`) headers. Because the HMAC never covered those headers, the signature still validates, and `Registry.process` passes the attacker-chosen `shop` value into `WebhookMetadata` and on to the app's handler as if Shopify itself asserted it. If the host application uses this `shop` value to select per-tenant data/credentials (a common and expected pattern per the gem's own webhook documentation), this results in cross-tenant data confusion/access — one shop's webhook payload being attributed to and processed under a different shop's identity.

### Likelihood Explanation
Exploitation requires the attacker to possess a valid body+HMAC pair for the webhook endpoint at least once; for many topics (e.g. `orders/create`, `app/uninstalled`) an attacker who runs their own store connected to the app can trivially generate one themselves and then relabel it as belonging to a victim shop, since the shop header is fully attacker-controlled and unauthenticated relative to the signature. This makes the attack straightforward for anyone with basic access to the app (a merchant/dev store), not requiring any secret leakage.

### Recommendation
Bind the tenant-identifying fields (`shop`, and ideally `topic`/`webhook_id`) into the HMAC-covered material, or otherwise cryptographically verify `shop` before trusting it — e.g. by making `Webhooks::Request#to_signable_string` include the shop/topic headers similar to `AuthQuery#to_signable_string`, or by requiring the host app to independently confirm the source shop's identity/registration (session lookup) before acting on `WebhookMetadata#shop`. At minimum, document prominently that `shop` in `WebhookMetadata` is unauthenticated and must not be trusted for tenant routing without additional verification.

### Proof of Concept
1. Attacker's own connected shop `attacker.myshopify.com` receives a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under `api_secret_key`), `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends this exact `B`/`H` to the app's webhook endpoint but changes the header to `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `H` against `B` (`to_signable_string` = raw body only) — the shop header is irrelevant to signature validation: [6](#0-5) 
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)`, and the app processes attacker-controlled data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
