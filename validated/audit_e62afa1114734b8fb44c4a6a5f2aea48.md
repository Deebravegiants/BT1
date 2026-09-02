## Title
Webhook Shop-Domain Header Not Covered by HMAC Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the `shop` (tenant identifier) is read from an HTTP header that is never included in the signed material. `Webhooks::Registry.process` trusts this unauthenticated header to identify which merchant/tenant a webhook belongs to. Any user who can obtain one genuine, validly-signed webhook for their own store can replay it against the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a different (victim) shop, and the gem's HMAC check still passes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from unauthenticated request headers: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `hmac(secret, to_signable_string)`, i.e. `hmac(secret, raw_body)`, against the received signature — it never binds the `shop` header into that computation: [3](#0-2) 

`Registry.process` then trusts the header-derived `shop` to build the `WebhookMetadata` handed to the host app's handler, after only checking the body HMAC: [4](#0-3) 

The identity binding that should hold is:
`shop_that_produced_the_signature == shop_used_to_route/act_on_the_webhook`

What is actually checked is only:
`hmac(secret, raw_body) == received_hmac`

Since `secret` (the app's `client_secret`) is shared across every shop that installs the app, and the `shop` field is entirely outside the signed bytes, the equality above does not hold: any bearer of one valid `(raw_body, hmac)` pair — obtainable by simply installing the app on one's own store — can present that same pair together with an arbitrary `X-Shopify-Shop-Domain` value and it will still validate successfully.

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged user who installs the target app on their own (attacker-controlled) shop receives genuine webhooks signed with the app's shared secret. By replaying the untouched body/HMAC with a substituted shop-domain header, they can make the host application (via this gem's `WebhookMetadata.shop`) believe the payload originates from a victim merchant's shop. Depending on which topics the host app has registered (e.g. `app/uninstalled`, `shop/redact`, `customers/redact`, `orders/*`), this can drive the host app to uninstall/erase data for, or otherwise mutate state belonging to, a shop the attacker never installed the app on — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is moderate to high: obtaining a genuine `(raw_body, hmac)` pair requires nothing more than the attacker installing the target app on a store they control (a normal, unprivileged action), then replaying the captured HTTP request to the app's public webhook endpoint with one header value changed. No `api_secret_key`, access token, or privileged access is needed.

### Recommendation
Bind the tenant identity into the verified material: include the `shop-domain` header (and ideally `topic`/`webhook-id`) in `to_signable_string`, or independently verify that the shop named in the header matches a shop the app expects to receive webhooks for (e.g., cross-check against an installed-shop registry) before dispatching to handlers. At minimum, document that `WebhookMetadata#shop` is not cryptographically bound to the payload and must not be trusted for authorization decisions without additional verification by the host application.

### Proof of Concept
1. Attacker installs the target Shopify app on their own dev/test store `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook (e.g. `customers/redact`) to the app's endpoint with headers `X-Shopify-Hmac-Sha256: <valid-hmac>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and some JSON body.
3. Attacker captures the raw body and `X-Shopify-Hmac-Sha256` value unchanged, and re-sends the request to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `raw_body` — it accepts the replayed request as valid.
5. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and the host application acts on the attacker's payload as though it came from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
