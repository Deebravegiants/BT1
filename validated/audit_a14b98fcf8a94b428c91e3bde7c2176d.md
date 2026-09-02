This confirms the finding. The webhook HMAC (`lib/shopify_api/webhooks/request.rb`) is computed only over `@raw_body` via `to_signable_string`, while the `topic`, `shop`, `webhook_id`, and `api_version` fields — all read straight from attacker-controllable HTTP headers via `shopify_header` — are never included in the signed material, and `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-190`) trusts them anyway.

### Title
Webhook shop/topic identity not bound to HMAC, enabling cross-tenant webhook forgery via header substitution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity solely by HMAC-checking the raw request body [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` to dispatch the payload to a handler are pulled directly from HTTP headers and are never part of the signed string [2](#0-1) .

### Finding Description
`HmacValidator.validate` computes `computed_signature = compute_signature(verifiable_query.to_signable_string, secret)` and compares it against `verifiable_query.hmac` [3](#0-2) . For webhook `Request` objects, `to_signable_string` returns only `@raw_body` [1](#0-0) ; it never incorporates `shop`, `topic`, or `webhook_id`, all of which are read verbatim from the `X-Shopify-*` headers [2](#0-1) .

`Registry.process` then validates only the body's HMAC and immediately trusts the header-derived `shop` and `topic` to select the handler and to construct `WebhookMetadata` that is handed to app code: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) .

The gem's own tests demonstrate the equality that is actually enforced: `hmac = OpenSSL::HMAC.digest(sha256, secret, "{}")` is a fixed value for any request whose body is `"{}"`, independent of shop or topic [5](#0-4) . This proves that the binding actually enforced is `hmac == HMAC(secret, body)`, not `hmac == HMAC(secret, body ‖ shop ‖ topic)` as the dispatch logic implicitly assumes.

Because the app's `api_secret_key` (`client_secret`) is shared across every shop that has the app installed, an unprivileged party who controls one shop with the app installed can legitimately receive a genuinely-signed webhook whose body is empty or otherwise attacker-influenced/predictable (many mandatory/compliance topics — `shop/redact`, `customers/redact`, `customers/data_request`, `app/uninstalled` — carry minimal or `"{}"` bodies, see `MANDATORY_TOPICS` [6](#0-5) ). That attacker can capture the `(body, hmac)` pair from their own legitimate webhook delivery, then replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, and `X-Shopify-Webhook-Id` headers to name a victim shop and a topic of the attacker's choosing. `HmacValidator.validate` still returns true because it only checks the (unchanged) body against the (unchanged) HMAC, and the resulting `WebhookMetadata` falsely attributes the event to the victim's tenant, invoking the app's handler logic (e.g. a GDPR redact handler, or the uninstall/deactivation handler) as if the victim shop had triggered it.

### Impact Explanation
This is a cross-tenant identity-binding break: the gem authenticates *bytes* (the raw body) but the application logic acts on *headers* (`shop`, `topic`) that were never covered by that authentication. An attacker can cause the host application to execute shop-scoped business logic (data deletion for compliance topics, uninstall handling, inventory/order processing depending on what handlers are registered) under an arbitrary victim shop identity, without ever possessing that shop's credentials. This matches the Critical "cross-tenant access" category.

### Likelihood Explanation
Requires only that the attacker control one shop that has the app installed (a normal, unprivileged merchant) and that at least one webhook topic delivers a body that is empty, static, or otherwise reproducible/attacker-influenced — true for the mandatory compliance topics that every app using this gem must support [6](#0-5) . No secrets, TLS interception, or social engineering are needed.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the value that is HMAC-verified (or independently re-derive/verify them, e.g. by requiring the `shop` used for dispatch to come from a lookup keyed by a value that *is* covered by the signature, or by including the headers in `to_signable_string`). At minimum, document that `shop`/`topic` are unauthenticated and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker registers their own shop `attacker.myshopify.com` with the target app installed.
2. Shopify delivers a legitimate webhook for a mandatory topic (e.g. `customers/redact`) with body `"{}"` and a valid `X-Shopify-Hmac-Sha256` header computed as `HMAC-SHA256(client_secret, "{}")`.
3. Attacker captures this `(body="{}", hmac=X)` pair.
4. Attacker sends a forged HTTP request to the app's webhook endpoint with:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: customers/redact` (or any topic whose handler the attacker wants to trigger)
   - `X-Shopify-Hmac-Sha256: X`
   - body: `"{}"`
5. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(secret, "{}") == X` [7](#0-6) .
6. `Registry.process` dispatches to the `customers/redact` handler with `shop: "victim-shop.myshopify.com"` [4](#0-3) , causing the app to execute redaction/business logic against the victim tenant on the attacker's command.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
```

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

**File:** test/webhooks/registry_test.rb (L16-30)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
```
