## Title
Webhook HMAC only signs the raw body, letting the `shop-domain`, `topic`, `webhook_id` and `api_version` headers be forged to spoof cross-tenant webhook attribution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and is validated via `Utils::HmacValidator.validate`, exactly like the OAuth `AuthQuery`. But unlike `AuthQuery#to_signable_string`, which binds `code`, `host`, `shop`, `state`, and `timestamp` into the signed string, `Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id` and `api_version` are all read straight off unauthenticated HTTP headers and never mixed into the HMAC input: [2](#0-1) 

`Registry.process` trusts these header-derived values directly after HMAC validation passes: [3](#0-2) 

### Finding Description
`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to `verifiable_query.hmac`: [4](#0-3) 

For `Webhooks::Request`, `to_signable_string` is only `@raw_body`. This means the equality the HMAC is supposed to enforce is:

`HMAC(secret, raw_body) == received_hmac`

but the value the application actually trusts as the tenant identity is:

`request.shop == headers["x-shopify-shop-domain"]` (or `shopify-shop-domain`)

These two are never bound together. Any request whose body byte-for-byte matches a body that was legitimately HMAC-signed by Shopify for the app's client secret will pass `Utils::HmacValidator.validate`, regardless of what `shop-domain`, `topic`, `webhook-id`, or `api-version` headers are attached to it.

An unprivileged internet user can obtain such a legitimately-signed `(body, hmac)` pair simply by installing the target app on their own (attacker-controlled) development store — this is normal, unprivileged app-installation activity, requiring no `api_secret_key`, access token, or leaked credential. Shopify will deliver real webhooks (e.g. `app/uninstalled`, `customers/data_request`, `shop/redact`) to the app's public webhook endpoint with a valid HMAC computed over the attacker's own shop's body.

The attacker can then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) to name a **different, victim shop**. `Utils::HmacValidator.validate(request)` still succeeds because it only checks the raw body against the HMAC, and `Registry.process` will build `WebhookMetadata` and invoke the app's handler with `shop: <victim-shop>` even though the payload actually originated from the attacker's own store: [3](#0-2) 

Because the gem's own documentation tells app authors that `data.shop` is the trustworthy "shop domain of the webhook" once `Registry.process` succeeds, this breaks the tenant-identity binding the HMAC is meant to guarantee: `shop authenticated by HMAC` ≠ `shop attributed to the event by the handler`.

### Impact Explanation
This directly enables cross-tenant confusion: a caller can make a real (HMAC-valid) webhook event, generated for the attacker's own tenant, be processed by the host app as if it belonged to an arbitrary victim shop (or under an arbitrary registered topic). Depending on how the host app's webhook handler uses `data.shop`/`data.topic` (e.g. marking a shop as uninstalled, purging/redacting a victim shop's data, updating billing/session state keyed by shop), this can cause state-changing, tenant-scoped actions to be executed against a shop the attacker does not control — a cross-tenant impact, matching the "Critical: cross-tenant access" category.

### Likelihood Explanation
Likelihood is realistic: obtaining a legitimately HMAC-signed webhook body requires nothing more than installing the public app on any store (including a free/dev store the attacker controls), which is available to any unprivileged internet user. Forging the destination shop/topic headers on the replayed HTTP request requires no cryptographic secret at all, since the HMAC never covers them.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into `Request#to_signable_string` (or otherwise verify them cryptographically, e.g. by including them in the HMAC input string similarly to `AuthQuery`), so that a valid HMAC can only be produced for the exact combination of body and identifying headers that Shopify actually sent.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (no privileged access needed).
2. Shopify sends a legitimate webhook to the app's endpoint, e.g.:
   ```
   POST /webhooks/callback
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: <id>
   x-shopify-api-version: 2024-01

   {}
   ```
3. Attacker captures this request and replays it to the same endpoint, changing only the shop header:
   ```
   POST /webhooks/callback
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <same valid-hmac-of-body>   # body unchanged
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: <id>
   x-shopify-api-version: 2024-01

   {}
   ```
4. `Utils::HmacValidator.validate(request)` returns `true` because it only hashes `@raw_body`, per `Request#to_signable_string`: [1](#0-0) 
5. `Registry.process` invokes the app's `app/uninstalled` handler with `shop: "victim-shop.myshopify.com"`, causing the host app to treat `victim-shop` as uninstalled/redacted even though the event actually came from `attacker-shop`.

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
