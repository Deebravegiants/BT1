Confirmed: `Registry.process` only checks `Utils::HmacValidator.validate(request)`, which delegates to `request.to_signable_string` = `@raw_body` only, and the `shop` value used to build `WebhookMetadata` is read straight from the `shopify-shop-domain` HTTP header, entirely outside the HMAC computation. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook shop-domain header not covered by HMAC allows cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying the HMAC of the raw request body, but the `shop` identity that the handler subsequently trusts is read from an HTTP header that is never included in the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [3](#0-2) 

`HmacValidator.validate_signature` computes the HMAC purely over that signable string (the body) with the app's `api_secret_key`: [5](#0-4) 

`Registry.process` accepts the webhook once that body-only HMAC check passes, then constructs `WebhookMetadata` using `request.shop`, which is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header — a value that was never part of the signed bytes: [1](#0-0) [6](#0-5) 

Shopify computes the webhook HMAC using the app's `client_secret`, which is identical for every shop that has installed the app — it is not shop-specific. Consequently, the equality the gem implicitly relies on is:

`bytes verified by HMAC == bytes the handler treats as tenant-identifying`

but this equality is false: the HMAC only proves "this body was signed with the app secret", while `request.shop` (the tenant identity handed to `WebhookMetadata`/`WebhookHandler#handle`) comes from an unauthenticated header. Any party who can obtain one validly-signed webhook body+HMAC pair for the app (e.g., by installing the app on their own shop and triggering a webhook with attacker-influenced body content) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim shop domain in the `shopify-shop-domain` header. `Utils::HmacValidator.validate` still returns `true` (body/secret pair is genuine), and `Registry.process` dispatches the handler with `shop: request.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary the webhook processing pipeline is supposed to enforce: an attacker can make the host application process attacker-controlled event data under a victim shop's identity, since the shop presented to `WebhookHandler#handle`/`WebhookMetadata` is not bound to the same bytes verified by the HMAC. This is a cross-tenant access primitive delivered entirely through this gem's `Registry.process`/`Request` API — no leaked credentials, no TLS interception, and no reliance on host-app misuse (the gem itself never binds shop to the signed payload).

### Likelihood Explanation
Likelihood is High for any app: the attacker only needs their own legitimate installation of the target app (a normal capability for anyone able to install a public Shopify app) to obtain valid signed webhook bodies for arbitrary attacker-influenced content, then replay them with a spoofed shop header at the app's public webhook endpoint.

### Recommendation
Bind the shop identity into the verified material: include the `shop-domain` header (and ideally `topic`/`webhook-id`) in the string that is HMAC-verified, or independently verify that `request.shop` corresponds to a shop actually associated with the currently processed installation/session before dispatching `WebhookHandler#handle`. At minimum, `Utils::HmacValidator` should validate a canonical representation that incorporates the shop-domain header rather than only the raw body.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) with body content of their choosing (order line items, note attributes, etc.).
2. Shopify sends the webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`, and the attacker-controlled JSON body.
3. Attacker captures the raw body and its valid HMAC, then re-sends an HTTP POST to the same endpoint with an unmodified body/HMAC pair but with the header changed to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks body-against-secret; `request.shop` (now `victim-shop.myshopify.com`) is passed to `WebhookMetadata`, and the handler executes as though the event legitimately originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
