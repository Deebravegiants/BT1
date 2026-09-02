### Title
Webhook HMAC validation signs only the raw body, allowing an attacker to replay a legitimately-signed webhook payload against a spoofed `shop-domain` header, causing cross-tenant webhook processing - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/utils/hmac_validator.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, excluding the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers from the HMAC-covered content. `Utils::HmacValidator.validate` verifies solely that this body was signed with the app's `api_secret_key`, and `Webhooks::Registry.process` then dispatches the (unauthenticated) `shop`, `topic`, and `webhook_id` header values straight into the handler as trusted tenant-identifying metadata. This breaks the intended binding `hmac == HMAC(secret, body ∥ shop)`; in reality it is only `hmac == HMAC(secret, body)`, so the `shop` used for tenant attribution is never bound to the signature.

### Finding Description
The webhook HMAC is computed and verified exclusively over the raw request body: [1](#0-0) 

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

The `shop`, `topic`, and `webhook_id` accessors read directly from HTTP headers with no cryptographic tie to the body or signature: [2](#0-1) 

`HmacValidator.validate`/`validate_signature`/`compute_signature` only ever operate on `verifiable_query.to_signable_string` (i.e., the raw body for webhooks) and the app's shared secret — they never incorporate the shop header: [3](#0-2) 

`Registry.process` gates on this body-only HMAC and then unconditionally forwards the header-derived `shop` (along with `topic`/`webhook_id`) to the app's handler as trusted tenant context: [4](#0-3) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

The identity-binding equality the library implicitly claims to enforce is:
`hmac_valid ⇒ (body, shop) originated together from Shopify for that shop`

What is actually enforced is only:
`hmac_valid ⇒ body was signed with api_secret_key` (no shop binding at all)

Because any merchant can trivially install the app on their own free/test store (no privileged credential, access token, or `api_secret_key` needed), they legitimately receive genuine `(raw_body, hmac)` pairs from Shopify for their own shop's webhook events. Since the app's webhook endpoint is a public HTTP endpoint, that same merchant can replay the captured `(raw_body, hmac)` pair directly to the endpoint while substituting the `shopify-shop-domain` header with any victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the header), and `Registry.process` passes the forged victim shop identity plus the attacker-chosen body content straight to the handler, which typically persists/acts on data keyed by `shop`.

### Impact Explanation
This is a cross-tenant access vulnerability: an unprivileged user (any merchant who installs the app once) can inject arbitrary attacker-chosen webhook payloads that the host application will attribute to a different, victim tenant (`shop`), because the gem's own verification primitive (`HmacValidator`/`Webhooks::Registry`) does not bind the `shop` (or `topic`/`webhook_id`) to the signed content. Depending on how the host app's webhook handlers use `WebhookMetadata#shop`/`#body` (e.g., updating stored order/product/customer data, or reacting to `app/uninstalled`), this allows cross-tenant data corruption or spoofed lifecycle events for a shop the attacker does not control — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high: no access token, `api_secret_key`, or any privileged credential is required. All that is needed is (1) a free Shopify store to install the app on and trigger any webhook topic with attacker-controlled body content, capturing the genuine `(raw_body, hmac)` pair, and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header — both trivially available to any internet user, no TLS interception or social engineering needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is cryptographically verified, e.g., include the `shop-domain` header in `to_signable_string` (Shopify does not sign it, so this requires either (a) validating the header against a caller-supplied allow-list of shops the app has actually installed offline tokens for, using the offline access-token/session lookup as the true tenant binding, rather than trusting the header value directly, or (b) documenting explicitly that host applications MUST authenticate the `shop` via their own session/token store before trusting `WebhookMetadata#shop`, and never use it as an unauthenticated tenant selector.

### Proof of Concept
1. Attacker registers a free/trial store `attacker.myshopify.com` and installs the target app, obtaining legitimate webhook delivery to the app's shared `/webhooks` endpoint for, e.g., the `orders/create` topic, with attacker-controlled order JSON as body.
2. Attacker captures the genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair from that delivery (e.g. via their own reverse proxy/logging, since it is delivered to the app's own infrastructure but the attacker controls the content and timing of the trigger).
3. Attacker sends a new POST request directly to the same public webhook endpoint, reusing the captured `raw_body` and `hmac` header unchanged, but replacing `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Webhooks::Request.new` parses headers/body as usual; `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only and it matches, since it never inspected the shop header (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Webhooks::Registry.process` dispatches `WebhookMetadata.new(shop: "victim.myshopify.com", body: attacker_json, ...)` to the app's handler (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the host application to process attacker-controlled data as if it belonged to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-40)
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

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
