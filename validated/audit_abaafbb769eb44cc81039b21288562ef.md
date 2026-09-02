This confirms the mandatory GDPR webhooks (`shop/redact`, `customers/redact`, `customers/data_request`) which carry destructive/data-handling semantics per shop, making the forgery attack practically damaging.

I have enough evidence to finalize the analog finding.

### Title
Webhook shop/topic identity is not covered by HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, and `HmacValidator` verifies the HMAC exclusively against that body. The `shop`, `topic`, `webhook_id`, and `api_version` values — all read from HTTP headers — are never included in the signed data, yet `Registry.process` trusts them to select the handler and to populate `WebhookMetadata#shop`, the field host apps use to key which merchant's data to act on.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it with `verifiable_query.hmac` [1](#0-0) . For webhook requests, `to_signable_string` is defined as simply `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the signature [3](#0-2) .

`Registry.process` validates only the HMAC, then dispatches using the unauthenticated `topic` and constructs `WebhookMetadata` with the unauthenticated `shop` header, which is the field host applications use to determine which tenant's records to update: [4](#0-3) .

Because a single app-level `api_secret_key` is used to sign webhooks for every shop that installs the app (not a per-shop secret), any party who can install the app on a shop they control (a normal, unprivileged action any developer can perform on a free/dev store) can capture a valid `(raw_body, hmac)` pair for a topic of their choosing — including one of the mandatory topics `shop/redact`, `customers/redact`, `customers/data_request` [5](#0-4) . That exact `(raw_body, hmac)` pair can then be replayed directly to the app's public webhook endpoint with the `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) headers rewritten to name a victim shop. `HmacValidator.validate` still succeeds because the signature only covers the body, and `Registry.process` will invoke the registered handler believing the event genuinely originated from the victim shop.

This is exactly the reported bug class: a field the application acts on (`shop`, used as the tenant/session key for the webhook handler) is not covered by the integrity check (HMAC), breaking the equality `shop authenticated by HMAC == shop used to select/act on tenant data`.

### Impact Explanation
This is a cross-tenant integrity break: an attacker can make the host application process a fabricated webhook event as if it came from any other merchant shop, without ever needing that shop's access token, session, or credentials — only knowledge of the target shop's domain (public information) and a self-obtained valid `(body, hmac)` pair from their own installation of the same app. For mandatory compliance webhooks such as `shop/redact` or `customers/redact`, this can trigger data-deletion/redaction logic against a victim shop's records inside the host app, and more generally lets an attacker inject arbitrary attacker-chosen webhook "events" (with attacker-controlled body content, since the signature only proves the body came from *some* real install, not that the shop/topic pairing is legitimate) attributed to any shop known to the app.

### Likelihood Explanation
Requires only: (1) the attacker's own ability to install the target app on a shop they control (trivial, free dev stores are self-service), (2) capturing one legitimate webhook delivery (any topic that shares a body shape with a mandatory topic, or simply the mandatory topics themselves which fire automatically on uninstall/GDPR requests), and (3) sending a crafted HTTP POST to the app's already-public webhook endpoint with rewritten headers. No secret material, TLS interception, or privileged account is needed — this is fully reachable by an unprivileged internet user who can self-serve an app install.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-verified signable string (or otherwise cryptographically bind them to the request), and/or have `Registry.process` reject requests where the shop is not one for which the host has an active, previously stored install/session before dispatching to handlers — do not treat the header-derived `shop` as an authenticated value on the basis of body-only HMAC success.

### Proof of Concept
1. Attacker installs the vulnerable app on their own controlled shop `attacker-shop.myshopify.com`, satisfying its OAuth flow legitimately.
2. Attacker triggers (or simply waits for) a `shop/redact` webhook delivery to their registered endpoint, capturing the raw request body `B` and the valid header `x-shopify-hmac-sha256: H` computed by Shopify using the app's single `api_secret_key`.
3. Attacker crafts a new HTTP POST to the same app's public webhook endpoint with body `B` (unchanged, so the HMAC in step 2 still validates), header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers, `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [6](#0-5) .
5. `Registry.process` invokes the `shop/redact` handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` [7](#0-6) , causing the host app to act on `victim-shop.myshopify.com`'s data despite the request never having been authenticated for that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
