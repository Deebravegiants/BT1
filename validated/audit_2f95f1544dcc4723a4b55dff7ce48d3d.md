### Title
Webhook shop-domain header is not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as fully authenticated once `Utils::HmacValidator.validate` succeeds, but the HMAC is computed only over the raw request body. The `shop` attribute — which the gem propagates to the app's handler as the tenant identity for the event — comes from an unsigned HTTP header and is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#hmac` and `#shop` are both derived independently from headers, but only `hmac` participates in signature verification: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and compares it against the received HMAC — the `shop` field is outside this computation entirely: [3](#0-2) 

`Registry.process` then trusts `request.shop` unconditionally as the tenant identity once the (body-only) HMAC check passes, and forwards it to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop attributed to the event == shop that produced the signed body`

But the code only proves `hmac == HMAC(client_secret, body)`; it never proves `shop header == shop that Shopify actually attributes to this body`. Since a single app's `client_secret` is shared across every shop that installs the app, any unprivileged user can install the app on their own store, capture one legitimately-signed webhook `(body, hmac)` pair from Shopify for their own shop, and then POST that same `(body, hmac)` pair to the target app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (the body and secret match), and `Registry.process` hands the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for verified webhooks (cross-tenant access). Depending on which mandatory/custom topic is targeted (e.g., `app/uninstalled`, `customers/redact`, `shop/redact`, or any subscribed business topic), an attacker can cause the host application to process attacker-controlled body content attributed to an arbitrary victim shop — e.g., triggering session/token invalidation for the victim, mutating or deleting the victim's stored data keyed by `shop`, or injecting forged business events for a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is realistic for any developer/attacker who can install the target app on a shop they control (a normal, unprivileged path for public apps), since that grants them a stream of validly-signed `(body, hmac)` pairs for their own shop that remain valid regardless of the `shop` header value sent alongside them. No access to `api_secret_key`, TLS interception, or privileged accounts is required — only the ability to send an HTTP request to the app's public webhook endpoint with a forged header.

### Recommendation
Bind the `shop` (and other routing-relevant headers such as `topic`/`webhook_id`, if used for authorization decisions) into the signed material, or, at minimum, have `Registry.process`/`HmacValidator` cross-check `request.shop` against an expected/known shop (e.g., the shop tied to the session used to register the webhook) before dispatching to the handler, rejecting mismatches. Document clearly that `request.shop` is unauthenticated so host apps do not treat it as verified tenant identity, and consider validating it against Shopify's shop domain format/allowlist in addition to any session-based binding recommended in `docs/`.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`, subscribing to `app/uninstalled` (or any impactful topic).
2. Trigger the event on `attacker.myshopify.com` so Shopify delivers a webhook `POST` with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Capture `(B, H)` from the attacker's own endpoint/logs (fully within attacker's control, no interception needed).
4. Send a new `POST` to the target app's real webhook endpoint with the same body `B` and `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which passes because it only checks `B` and `H`; it then invokes the app's handler with `shop: "victim-shop.myshopify.com"`, causing the host app to act as if the event genuinely originated from the victim's store.

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
