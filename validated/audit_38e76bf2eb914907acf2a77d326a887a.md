The report's reentrancy bug class (an identity/authorization check separated from an object's later-used state) has a direct analog in this gem's webhook verification: the `shop` value the handler acts on is not covered by the HMAC that authenticates the webhook.

### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook by checking an HMAC over the raw request body only. It then trusts `request.shop`, which is read straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, and passes it to the app's handler as the shop identity for the event. Because the header is not part of the signed material, any party who can produce one valid `(body, hmac)` pair for the shared `api_secret_key` can replay that exact pair while substituting an arbitrary `shop-domain` header, and the library will accept it as an authentic webhook "from" that other shop.

### Finding Description
`Request#hmac` decodes the signature header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`shop` is read from a plain header that is not part of `to_signable_string`: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (the body) and compares it to the received signature, so the check only binds the *body* to the secret, never the shop-domain header: [4](#0-3) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` (the unauthenticated header value) to the app's handler as the trusted tenant identity: [5](#0-4) 

The equality that should hold is: `shop value authenticated by the HMAC == shop value delivered to the handler`. In reality: the HMAC authenticates only `{body}`, while the handler receives `{shop-domain header}`, an independently-controllable field. Since `api_secret_key` is shared across every shop that installs the app (not per-shop), a webhook payload legitimately generated for shop A carries a signature that remains valid no matter what `shop-domain` header accompanies it, because that header was never part of the signed input in the first place.

### Impact Explanation
This breaks the tenant-identity binding the whole webhook mechanism depends on: the app must be able to trust that a webhook event with a given `shop` came from that shop, since handlers commonly key their data lookups/writes on `WebhookMetadata#shop`. An attacker able to obtain one genuine `(raw_body, hmac)` pair (e.g., from their own shop's install, which is available to any unprivileged internet user who installs a public app) can relabel it to point at a victim shop, causing the host application to process attacker-controlled webhook data under a different tenant's identity — a cross-tenant confusion at the library layer. This maps to the "Critical - cross-tenant access" impact category since the shop-scoping guarantee the gem is supposed to provide to the webhook handler is bypassed.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop (available to any internet user for public apps), (2) capturing one webhook delivery (body + signature) sent to the attacker's own registered endpoint, and (3) resending that identical body/signature pair to the app's webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key`, tokens, or TLS interception is required — the attacker only needs a webhook that was legitimately signed for their own tenant.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or otherwise cryptographically bind the shop identity to the signed payload before it is handed to the handler, so that `request.shop` cannot be swapped independently of the signature that authenticated the payload.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; register a webhook handler and receive one real webhook delivery, e.g. headers `x-shopify-hmac-sha256: <sig>`, `x-shopify-shop-domain: attacker.myshopify.com`, body `{"id":1}`.
2. Replay the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replace the header with `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the signature over the (unchanged) body and it still matches, so `Registry.process` in `lib/shopify_api/webhooks/registry.rb` line 190 passes validation and invokes the handler with `shop: "victim.myshopify.com"` per `lib/shopify_api/webhooks/request.rb` lines 20-23, even though the payload never actually originated from Shopify for that shop.

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
