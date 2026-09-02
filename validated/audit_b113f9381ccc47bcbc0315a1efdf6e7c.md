### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` validates the authenticity of an inbound webhook using an HMAC computed only over the raw request body, while the `shop` (tenant) identity used by the handler is taken from an HTTP header that is completely outside the signed material. Any actor who possesses one valid `(body, hmac)` pair for the app's shared `api_secret_key` — e.g. a merchant who legitimately installed a public app and received a real webhook for their own store — can replay that pair while substituting the `shopify-shop-domain` header for a victim shop, and the library will accept it as an authentic webhook "from" the victim shop.

### Finding Description
`HmacValidator.validate` computes and compares the signature only over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns exclusively the raw HTTP body — the `shop`, `topic`, `webhook_id`, and `api_version` values are all pulled from separate, unsigned headers: [2](#0-1) 

`Registry.process` only checks that the HMAC of the body is valid, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The identity binding that should hold is: `shop_header == shop_that_the_HMAC_over_this_body_actually_belongs_to`. Because the signature covers only the body bytes and never the `shop` header, this equality is never checked. Any request whose body/HMAC pair is valid for the app's `api_secret_key` will be accepted regardless of which shop domain is asserted in the header, because the `api_secret_key` is shared by the app across all of its installed shops (it is not per-shop).

### Impact Explanation
This breaks the tenant boundary between merchants of the same app: an unprivileged party who is simply a legitimate installer of the app (no special access token, no leaked credentials) can obtain one authentic `(body, hmac)` pair by receiving a real webhook for their own store, then replay it to the app's webhook endpoint with the `shopify-shop-domain` header changed to a victim shop. The handler (`data.shop`) will process the request as if it genuinely originated from the victim tenant — e.g. attributing order/customer/app-uninstalled data to the wrong shop, or triggering shop-scoped business logic (billing, provisioning, data deletion on `app/uninstalled`) against a tenant that never sent that event. This is a cross-tenant identity confusion, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitability only requires the attacker to be a normal, unprivileged merchant who has installed the public app at least once (no `api_secret_key`, no access token, no privileged account needed) — they already legitimately possess one valid `(body, hmac)` pair for their own shop and can simply resend it with a forged `shop-domain` header. No brute force of the HMAC itself is needed since it is replayed verbatim.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material that `HmacValidator` verifies, or otherwise cryptographically tie the asserted shop header to the specific webhook delivery (for example, by validating the webhook against the shop for which it was registered/expected, or by including shop context in the signable string) before invoking the registered handler.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Attacker resends this exact request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but replacing `x-shopify-shop-domain: attacker.myshopify.com` with `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `@raw_body` (`B`) and compares to `H` — validation succeeds (`lib/shopify_api/webhooks/request.rb` `to_signable_string`, `lib/shopify_api/utils/hmac_validator.rb` `validate_signature`).
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the forged `shop-domain` header and invokes the app's handler as if `victim.myshopify.com` sent this webhook (`lib/shopify_api/webhooks/registry.rb` lines 188-200), achieving cross-tenant data/event confusion.

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
