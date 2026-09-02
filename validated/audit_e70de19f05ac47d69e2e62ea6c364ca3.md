### Title
Webhook shop-domain header is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, and `Utils::HmacValidator.validate` only verifies that body against the `hmac` header. The `shop-domain` header, which `ShopifyAPI::Webhooks::Registry.process` hands to the app's handler as the tenant identifier, is never part of the signed payload. Anyone who can obtain one valid `(body, hmac)` pair for the app (e.g., by installing the app on their own shop and capturing a legitimate webhook delivery) can replay that same body/HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The signature still validates because the shop is not covered by the HMAC, so `Registry.process` will hand the attacker-controlled body to the handler labeled as belonging to any shop the attacker chooses.

### Finding Description
`Registry.process` verifies the request solely via `Utils::HmacValidator.validate(request)` and then forwards `request.shop` (read straight from a header) to the handler without any cross-check that it matches the value used to produce the signature: [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body`, so the HMAC covers exactly the body bytes and nothing else, while `shop`, `topic`, and `webhook_id` are all pulled independently from headers that are never mixed into the signed string: [2](#0-1) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the body) and compares it to the received `hmac`, again with no shop binding: [3](#0-2) 

Because every shop that installs a given app shares the same `api_secret_key`, a valid `(body, hmac)` pair captured from any one merchant's webhook delivery remains valid regardless of which `shop-domain` header accompanies the replayed request. The equality the gem should enforce — "shop bound into the HMAC payload" == "shop delivered to the handler as the event's tenant" — does not hold; the shop delivered to the handler is taken from an unauthenticated header while the HMAC only authenticates the body.

### Impact Explanation
This breaks the tenant boundary that host applications rely on `WebhookMetadata#shop` to establish. An attacker who is a legitimate (even free/trial) merchant on the app can capture one authentic webhook for their own shop and replay its body+HMAC to the same public endpoint with the `shop-domain` header rewritten to a victim shop. Any host application that trusts `data.shop` to scope database writes, cache invalidation, inventory/order updates, or other tenant-specific side effects will apply the attacker's captured payload under the victim's tenant identity — a cross-tenant access/data-integrity issue.

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the target app on any shop (self-service, low privilege) to capture one genuine webhook body/HMAC pair, and (2) sending a crafted HTTP POST with that same body/HMAC but a different `shop-domain` header to the app's already-public webhook endpoint. No secrets, tokens, or elevated access are needed beyond what any user can obtain by using the app normally.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed payload, or otherwise cryptographically bind the `shop-domain` header to the request before it is trusted — e.g., verify the shop against a persisted expectation from session/registration state rather than the raw header value from an incoming HTTP request. At minimum, `Request#to_signable_string` should incorporate the shop header so `HmacValidator.validate` fails when the header is altered post-signing.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com` and receive a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `api_secret_key`).
2. Send a new POST request to the app's webhook endpoint with the identical body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `HmacValidator.validate(request)` which recomputes the HMAC over `B` only, matches `H`, and passes.
4. The handler receives `WebhookMetadata.new(... shop: "victim.myshopify.com", body: parsed(B) ...)`, causing the host app to process attacker-supplied data under the victim shop's tenant identity.

### Citations

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
