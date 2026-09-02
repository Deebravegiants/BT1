### Title
Webhook `shop` (and topic/api-version/webhook-id) fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `ShopifyAPI::Webhooks::Registry.process` trusts the `shop`, `topic`, `api_version`, and `webhook_id` attributes — all taken from unsigned HTTP headers — to attribute the delivered payload to a specific merchant/tenant. The HMAC validated by `Utils::HmacValidator.validate` only proves that the *body bytes* were signed with `api_secret_key`; it proves nothing about which shop the header claims the payload came from.

### Finding Description
`HmacValidator.validate` computes and compares the signature over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be only the raw request body: [2](#0-1) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are **not part of the signed material**: [3](#0-2) 

`Registry.process` verifies the HMAC and then immediately forwards `request.shop` (an unauthenticated header value) to the handler as the tenant identity for the event: [4](#0-3) 

The binding the gem is supposed to enforce is:
`shop_the_payload_is_attributed_to == shop_that_the_signing_secret_proves_authorship_for`

Because `shop` is excluded from `to_signable_string`, this equality is never checked. Any party who can obtain one genuinely-signed `(body, hmac)` pair — e.g. a merchant who has legitimately installed the app on their own store and therefore legitimately receives real Shopify webhook deliveries for it — can capture that pair and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` will still succeed (it only checks the body against the secret), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This breaks the tenant-isolation guarantee that webhook processing is scoped to the correct shop. Any application logic that uses `WebhookMetadata#shop` to route writes/reads (e.g., "update this shop's local order record", "look up this shop's session/access token") can be made to act on the wrong tenant's data using an attacker-controlled body, because the shop attribution is unauthenticated. This is a cross-tenant data-integrity/access issue driven directly by a signing-coverage gap in the gem.

### Likelihood Explanation
Exploitation only requires the attacker to control one legitimately-installed shop (a very low bar — any merchant who installs the app can generate real signed webhook deliveries for their own store) and the ability to send arbitrary HTTP requests with custom headers to the app's public webhook endpoint. No access token, `client_secret`, or privileged credential is required.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable content the HMAC is computed over, or otherwise cryptographically bind `shop` to the signed payload before it is exposed via `WebhookMetadata`, so that `Utils::HmacValidator.validate` cannot succeed for a body whose claimed shop was substituted after signing.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, allowed installation).
2. Shopify delivers a legitimate webhook to the app: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, HMAC(secret,B))` and POSTs it again to the same webhook endpoint, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb) recomputes `HMAC(secret, B)` and it still matches, since `B` and the secret are unchanged.
5. `Registry.process` (lib/shopify_api/webhooks/registry.rb:188-200) invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the host application to process attacker-controlled data as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
