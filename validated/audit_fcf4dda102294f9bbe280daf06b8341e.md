### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (from `x-shopify-shop-domain`/`shopify-shop-domain`) header is read independently and passed unverified to the webhook handler. Because the shop identity is not bound into the HMAC, a value that is *acted on* (the shop that the event is attributed to) is not the same value that is *cryptographically verified* (the body bytes). This breaks the equality `shop verified-by-HMAC == shop delivered-to-handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is derived purely from a header, entirely outside the HMAC computation: [2](#0-1) 

`Utils::HmacValidator.validate_signature` verifies the signature against `verifiable_query.to_signable_string` (i.e., only the body), using the app's `client_secret` (`Context.api_secret_key`): [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then immediately hands the *unverified* `request.shop` to the registered handler as the tenant identity for the event, without any additional binding check between the verified bytes and the claimed shop: [4](#0-3) 

Since the same `client_secret` is used to sign webhooks for *every* shop that installs the app, and many webhook topics carry small or identical bodies (e.g. `app/uninstalled` has an empty JSON body `"{}"`, as shown in the test fixtures), a request whose body+HMAC pair was genuinely produced for shop A is a byte-for-byte valid, HMAC-passing payload for any other shop's domain, because the `shop-domain` header value never enters the signable string. An attacker who has legitimately installed the app on their own shop (unprivileged relative to the target tenant) can capture one of these signed callbacks and replay it against the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop. `HmacValidator.validate` will pass (it only checks body bytes against the secret), and `Registry.process` will dispatch to the app's handler with `WebhookMetadata#shop` set to the victim's domain — a cross-tenant identity confusion entirely internal to this gem's verification logic.

### Impact Explanation
This is a cross-tenant boundary break at the library level: the gem asserts "this webhook body is authentic and this is the associated shop" via `Registry.process`, but the shop attribution is not covered by the same cryptographic check as the body. Any host application that trusts `WebhookMetadata#shop` returned by `Registry.process` (which is the gem's documented and intended usage) can be made to apply an attacker-controlled shop's events (e.g., uninstall/reinstall lifecycle signals, GDPR-style events, or app-specific webhook bodies with shared/identical schema) to a different, victim tenant, since the gem itself does not bind the two together. This satisfies the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation only requires the attacker to be an ordinary, unprivileged user of the app on their own store (installing the app is normally self-serve) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint with attacker-chosen headers — both trivially available to any internet user, with no access token, `client_secret`, or privileged account needed. The most reliable trigger is topics whose payload is invariant or predictable across shops (e.g., `app/uninstalled` with body `"{}"`), which is already demonstrated as an accepted, valid webhook shape in this codebase's own tests.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the HMAC-covered signable string, or otherwise cryptographically tie the `x-shopify-shop-domain` header to the verified payload before it is trusted (e.g., include header values in the signature computation used by `to_signable_string`, or require the host app to cross-check `request.shop` against an out-of-band verified tenant identifier before invoking handlers). At minimum, document prominently that `request.shop`/`WebhookMetadata#shop` is unauthenticated and must not be used as sole tenant discriminator, and consider raising in `Registry.process` if callers need cross-tenant guarantees.

### Proof of Concept
1. App is installed on attacker's own shop `attacker.myshopify.com`; Shopify sends a genuine `app/uninstalled` webhook with body `"{}"`, headers including `x-shopify-hmac-sha256: <valid HMAC over "{}">` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays this exact HTTP request to the app's webhook endpoint, only changing `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the headers/body; `Utils::HmacValidator.validate(request)` succeeds because it only checks `OpenSSL::HMAC.hexdigest(sha256, client_secret, "{}")` against the unchanged HMAC value: [5](#0-4) 
4. `Registry.process` dispatches to the app's handler with `WebhookMetadata.new(..., shop: request.shop, ...)` where `request.shop == "victim.myshopify.com"`: [6](#0-5) 
5. The host app's handler processes an "uninstall" (or other) event as if it originated from `victim.myshopify.com`, even though it never occurred for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
