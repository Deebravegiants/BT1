## Finding

### Title
Webhook `shop` identity is taken from an unauthenticated header while the HMAC only covers the request body, allowing shop/tenant spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `api_version`, `webhook_id`) values from HTTP headers, but the HMAC signature that `Webhooks::Registry.process` validates only covers the raw request body, never the headers. This breaks the identity binding `hmac(shop_header) == hmac(raw_body)` that the code implicitly assumes: the `shop-domain` header is *acted on* (passed straight into the handler as the tenant identity) but is never *covered by the HMAC*.

### Finding Description
`Webhooks::Request#hmac` and `#to_signable_string` are defined as: [1](#0-0) 

Concretely: [2](#0-1) 

`shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely outside of `to_signable_string`, which only returns `@raw_body`: [3](#0-2) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac-sha256` header — it never authenticates the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers: [4](#0-3) 

`Webhooks::Registry.process` then trusts `request.shop` as the tenant identity and forwards it, unauthenticated, into the app's handler: [5](#0-4) 

Because only the raw body is signed, an unprivileged internet user who has ever observed one legitimate webhook delivery for *any* shop (e.g., their own installed test shop) possesses a `(raw_body, hmac-sha256)` pair that remains cryptographically valid forever, since the message digest is independent of headers. They can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header with an arbitrary victim shop's domain. `HmacValidator.validate` will report success (it never looks at the shop header), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding failure: `shop_header == authenticated_shop` does not hold. Any app that uses `WebhookMetadata#shop` to select which merchant's data/session/access token to act on (a documented, expected usage of this gem's webhook API) can be tricked into associating attacker-supplied data with another tenant's shop identity, or into triggering shop-scoped side effects (e.g. cache invalidation, data writes, internal book-keeping keyed by shop) under a spoofed tenant. This matches the "cross-tenant access" Critical impact category, since the trust boundary between tenants is broken purely by header manipulation with no access token or secret required.

### Likelihood Explanation
Likelihood is high for an unprivileged internet user: they only need to have received (or captured) one legitimate webhook body+HMAC pair — which is trivial for an attacker who installs the target app on their own test shop — and can then freely relabel that payload as coming from any other shop domain by editing the plain-text HTTP header, since headers are never covered by the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signed material, or independently verify that the `shop-domain` header corresponds to a shop session/installation known to the app before trusting it; at minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant identifier.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives one legitimate webhook, capturing `raw_body` and the `shopify-hmac-sha256` header value.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body` and `shopify-hmac-sha256`, but sets `shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) recomputes HMAC over `raw_body` only and it matches → validation passes.
4. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, even though the payload never actually came from Shopify for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
