This confirms the vulnerability structure precisely.

### Title
Webhook `shop` and `topic` fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw request body, then dispatches the handler using the `shop` value taken from an HTTP header that is never included in that signature. [1](#0-0)  Because `Request#to_signable_string` returns only `@raw_body`, and `Request#shop` / `Request#topic` are pulled straight from the `x-shopify-shop-domain` / `x-shopify-topic` headers, these fields are "acted on but not covered by the HMAC" — mirroring exactly the analog pattern called out in the rules (a field used by the application but excluded from the cryptographic binding). [2](#0-1) [3](#0-2) 

### Finding Description
The `HmacValidator.validate` method computes and compares an HMAC solely over `verifiable_query.to_signable_string`: [4](#0-3)  and the `VerifiableQuery` interface only requires `hmac` and `to_signable_string` — no method binds `shop` or `topic` into the signed payload. [5](#0-4) 

For webhook requests, `Request#to_signable_string` returns the raw request body only, while `Request#shop`, `Request#topic`, `Request#api_version`, and `Request#webhook_id` are read directly, unauthenticated, from HTTP headers: [6](#0-5) 

`Registry.process` then does: validate HMAC of body → look up handler by `request.topic` → invoke the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`. [1](#0-0) 

The identity binding that should hold is:
**shop bytes verified by HMAC == shop value the application uses to attribute/store the webhook payload.**

In this code, HMAC only proves *"the body was produced with knowledge of `api_secret_key`."* It proves nothing about which shop or topic that body belongs to. Since Shopify computes the HMAC the same way for every shop using a given app's shared `client_secret`, any merchant who has legitimately installed the app can capture one authentic webhook delivery (raw body + valid `x-shopify-hmac-sha256`) sent to their own store, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` (and/or `x-shopify-topic`) header value. `HmacValidator.validate` still succeeds (it never looks at the shop/topic headers), and `Registry.process` hands the handler a `WebhookMetadata` object whose `shop` is the attacker-chosen victim shop domain rather than the shop that actually produced the body. [7](#0-6) 

Any host application that uses `WebhookMetadata#shop` to key data writes, tenant lookups, or GDPR/redact actions (the library's own `MANDATORY_TOPICS` include `shop/redact`, `customers/redact`, `customers/data_request` [8](#0-7) ) will process attacker-controlled data under another tenant's identity — a direct cross-tenant integrity/confidentiality break, reachable by any unprivileged actor who can install the app on their own shop and send one HTTP POST to the app's public webhook endpoint.

### Impact Explanation
This breaks tenant isolation (cross-tenant access), matching the Critical impact category defined in scope: an attacker who is merely a legitimate but unprivileged app installer on their own shop can cause the application to attribute webhook data/events to an arbitrary victim shop domain, without needing the app's `client_secret`, an access token, or any privileged access. Depending on how the host app consumes `WebhookMetadata#shop` (e.g., updating order/customer records, triggering redaction, or driving business logic keyed by shop), this can lead to data corruption, spoofed events, or unauthorized actions attributed to another merchant's store.

### Likelihood Explanation
Likelihood is high for any app that both (a) uses this gem's `Webhooks::Registry`/`Request` for webhook handling and (b) trusts `WebhookMetadata#shop` (or `#topic`) for tenant attribution without independently re-validating it against a known/installed-shop list. The only prerequisite is installing the app on an attacker-controlled shop to obtain one valid signed webhook body — a normal, unprivileged capability. No secrets, tokens, or elevated access are required to construct the forged request, since the header fields are simply never part of the cryptographic proof.

### Recommendation
Bind `shop` (and ideally `topic`) into the value that is HMAC-verified, or independently authenticate them: e.g., have `Request#to_signable_string` include the `shop-domain` and `topic` headers in the signed material (matching what Shopify actually signs, if it does), or have `Registry.process` cross-check `request.shop` against a shop already known/authorized for the given `webhook_id`/topic before invoking the handler. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated header values and must not be trusted for tenant attribution without additional verification by the host application.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged action).
2. Shopify sends a legitimate webhook to the app's endpoint:
   ```
   POST /webhooks
   x-shopify-topic: customers/update
   x-shopify-hmac-sha256: <valid HMAC of raw body B>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: B
   ```
3. Attacker captures `B` and the valid `x-shopify-hmac-sha256` value (they own this webhook delivery).
4. Attacker replays the same request to the app's webhook endpoint, changing only the shop header:
   ```
   POST /webhooks
   x-shopify-topic: customers/update
   x-shopify-hmac-sha256: <same valid HMAC of body B>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: B
   ```
5. `Utils::HmacValidator.validate` succeeds because it only checks the body against `api_secret_key`. [9](#0-8) 
6. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "customers/update", body: <attacker-controlled data B>, ...)`, causing the host application to act on `B` as though it were legitimately produced by `victim-shop.myshopify.com`. [1](#0-0)

### Citations

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L6-16)
```ruby
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```
