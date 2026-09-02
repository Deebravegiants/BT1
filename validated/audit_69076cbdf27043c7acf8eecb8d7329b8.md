### Title
Webhook `shop-domain` and `topic` headers are trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, and that validation only covers the raw request body — never the `shop-domain` or `topic` headers that are subsequently used to route the payload to a handler and to stamp the tenant identity (`shop`) delivered to application code.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes/verifies the signature exclusively over that signable string: [2](#0-1) 

`Registry.process` uses this HMAC check as the sole authentication gate, then dispatches based on `request.topic` and forwards `request.shop` (both read from headers, not the signed body) straight into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identity: [3](#0-2) 

`shop` and `topic` are read directly from HTTP headers: [4](#0-3) 

`WebhookMetadata.shop` is the only tenant identifier surfaced to the handler, and it is populated from this unauthenticated header: [5](#0-4) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop acted on by the handler`

In this gem, the HMAC only authenticates the **body**; the **shop** (and **topic**) fields the handler acts on are unauthenticated header values. `OpenSSL::HMAC` with the app's `client_secret` produces the same digest for the same raw body regardless of which shop header accompanies it, since the shop identity is never mixed into the signed material. Any two webhook deliveries carrying byte-identical bodies (which is common — many Shopify webhook topics, e.g. `app/uninstalled`, `shop/redact`, or topics with sparse/empty JSON payloads, produce identical or attacker-predictable bodies across different shops) will have **identical valid HMAC signatures** computed with the single app-wide secret. Consequently, a webhook payload+HMAC pair legitimately received by an app for Shop A can be replayed by anyone able to reach the app's webhook endpoint (this is an internet-reachable HTTP endpoint by design) with the `shop-domain` header rewritten to Shop B and/or the `topic` header rewritten to a different registered topic, and `Registry.process` will accept it as valid and dispatch it to the handler labeled as Shop B's event.

This is the exact bug class described in the report, transposed into this gem's terms: a field the application acts on (`shop`, used as the tenant/session key for all downstream handler logic) is not covered by the authenticity check (`HmacValidator`/`to_signable_string`) that is supposed to bind the message to its source.

### Impact Explanation
This enables cross-tenant confusion at the trust boundary the gem is responsible for: the host application relies on this gem's `Registry.process`/`WebhookMetadata` to assert "this event body is authentically from Shopify and belongs to shop `X`." Because `shop` is not bound to the signature, an attacker who has (or can obtain) any single valid `(body, hmac)` pair for their own installed shop can forge delivery for a different merchant's `shop` value with that same body, or reroute it to a different `topic` handler. Depending on the app's own webhook handler logic (e.g. deprovisioning on `app/uninstalled`, redaction on `shop/redact`/`customers/redact`, order/customer data ingestion keyed by `shop`), this can be leveraged to trigger tenant-scoped side effects (deletion, redaction, data corruption) against a shop the attacker does not control — a cross-tenant access impact as called out in the Critical/High severity bar. The exact blast radius is bounded by what the consuming application does with `WebhookMetadata#shop`/`#topic`, which is outside this gem, but the gem is the component that fails to bind the identity it advertises as verified.

### Likelihood Explanation
Exploitation requires the attacker to control (or observe) at least one genuinely-signed `(body, hmac)` pair for some shop — trivially available to any merchant/developer who installs the target app on their own store, since Shopify will deliver real signed webhooks to them. From there, forging the header values is a matter of a normal HTTP POST to the app's public webhook endpoint; no `client_secret`, access token, or other privileged credential is needed, only knowledge of a previously-observed valid payload/signature pair for a topic whose body is empty, static, or otherwise reproducible/predictable (several mandatory topics fit this profile). This keeps the analog within the "unprivileged internet user" threat model required by scope.

### Recommendation
Bind the header-derived identity fields into the signed material, or otherwise cryptographically tie `shop-domain`/`topic` to the signature, before trusting them for routing/session purposes. Concretely, `Request#to_signable_string` should incorporate `shop`, `topic`, and `webhook_id` (in addition to the raw body) into the string verified by `HmacValidator`, or the gem should document/enforce that callers must independently verify `shop` against a known/expected shop before acting on `WebhookMetadata`. At minimum, `Registry.process` should not treat header-derived `shop`/`topic` as authenticated simply because the body's HMAC validates.

### Proof of Concept
1. Attacker installs the target Shopify app on their own controlled shop `attacker-shop.myshopify.com` and registers/receives a webhook for a topic with a static/empty body, e.g. `shop/redact` with body `{}` (`test/webhooks/registry_test.rb:16-28` shows `{}` bodies are the norm in this gem's own test fixtures, confirming small/static bodies are common): [6](#0-5) 
2. Attacker records the legitimately delivered `x-shopify-hmac-sha256` value Shopify computed over body `{}` using the app's real `client_secret`.
3. Attacker sends a new HTTP POST to the same app webhook endpoint with the identical body `{}` and the identical (still-valid) `hmac-sha256` header, but with `x-shopify-shop-domain: victim-shop.myshopify.com` (a shop the attacker does not own) and/or `x-shopify-topic: app/uninstalled`.
4. `ShopifyAPI::Webhooks::Request.new` accepts it (headers present) and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `Digest.hexencode(...)` against `to_signable_string` (`@raw_body`) — it passes because the body `{}` is unchanged: [7](#0-6) 
5. The handler registered for the (attacker-chosen) topic is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though that shop never sent this event — the app now performs shop-`victim-shop`-scoped logic (e.g. redaction/uninstall handling) on the attacker's command.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** test/webhooks/registry_test.rb (L16-28)
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
```
