### Title
Webhook `shop-domain` Header Not Covered by HMAC — Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` value it hands to the application's handler is read from the `X-Shopify-Shop-Domain` header, which is never included in the signed payload. An attacker who controls a legitimate installation of the app (and can therefore obtain a body+HMAC pair signed with the app's own `api_secret_key`) can replay that exact body/HMAC while substituting an arbitrary `shop-domain` header value, and the library will accept it as an authentic webhook "from" the spoofed shop.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing the HMAC over `to_signable_string` and comparing it to the supplied `hmac`. [1](#0-0) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only the raw body, and `hmac` is decoded strictly from the `hmac-sha256` header — none of `topic`, `shop-domain`, `api-version`, or `webhook-id` participate in the signature: [2](#0-1) 

`Registry.process` validates the request using only this body-bound HMAC, then immediately trusts `request.shop` (sourced from the unauthenticated header) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The equality the library implicitly claims is: `shop used by handler == shop the HMAC authenticates`. In reality the HMAC authenticates only the body bytes; it says nothing about which shop sent it. Because the secret (`Context.api_secret_key`) is shared across all shops that install the app, any shop that legitimately receives a webhook (or otherwise obtains one valid body+HMAC pair, e.g. by triggering a webhook on their own store) can capture that valid `(raw_body, hmac)` pair and resubmit it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), so `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` even though the payload was never generated for, or by, that shop.

### Impact Explanation
This breaks the tenant-identity binding relied on by any app whose webhook handler branches or persists data keyed off `WebhookMetadata#shop` (e.g., updating the victim's local shop record, canceling a victim's mandatory-topic data, or triggering shop-scoped side effects) — a cross-tenant access scenario, since one merchant's authenticated webhook traffic can be relabeled to impersonate another tenant.

### Likelihood Explanation
Exploitation requires only: (1) the attacker installs (or already has) the app on their own shop and can capture one raw webhook body plus its `X-Shopify-Hmac-Sha256` header — both delivered to their own server in the normal webhook flow — and (2) the ability to POST to the app's public webhook endpoint with a modified `shop-domain` header, which requires no secret material at all. This is fully reachable by any unprivileged existing app-installer, without needing `api_secret_key`, an access token, or any credential leakage.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the authenticated material, e.g. either include the `shop-domain`/`topic` header values in `to_signable_string` verification against an app-side allow-list of the shop's own registered installation, or independently verify that `request.shop` corresponds to a shop with a known, stored session before acting on the webhook — do not treat the `X-Shopify-Shop-Domain` header as trusted solely because the body HMAC validated.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers any subscribed webhook topic (e.g. updates a product), causing Shopify to POST a body `B` with header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the shared `api_secret_key`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` to the app's webhook endpoint.
2. Attacker intercepts/records `(B, H)`.
3. Attacker crafts a new HTTP POST to the same webhook endpoint with identical body `B` and identical `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation passes. [4](#0-3) 
5. The handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the payload and signature were never produced for that shop.

### Citations

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
