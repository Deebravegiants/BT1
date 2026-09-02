## Finding

### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) header values are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` purely from unauthenticated HTTP headers, while the HMAC signature that `ShopifyAPI::Utils::HmacValidator` verifies covers only the raw request body via `to_signable_string`. Because the `shop` value that `ShopifyAPI::Webhooks::Registry.process` hands to the application's webhook handler is never bound to the HMAC, an attacker who owns any shop that can legitimately trigger a webhook to the same endpoint (using the same app `client_secret`, which is shared across all installs of the app) can replay that valid `(body, hmac)` pair while forging the `x-shopify-shop-domain` header to any other merchant's domain, and the signature check still passes.

### Finding Description
`Request#hmac` reads the signature from the `hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read straight from headers with no cryptographic tie to the signature: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` compute and compare the HMAC solely against `verifiable_query.to_signable_string` (the body), never incorporating `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` trusts `request.shop` (and `topic`/`webhook_id`/`api_version`) after only confirming the HMAC over the body is valid, then forwards it unchanged to the app's handler as authenticated shop context: [4](#0-3) 

The identity binding that should hold is: `shop asserted in header == shop the HMAC was computed for`. Because the HMAC is computed only over `client_secret + raw_body`, and `raw_body` is not shop-specific for many webhook topics (e.g. `shop/redact`, `customers/data_request`, or any topic whose payload does not embed the domain, or where the attacker's own shop payload is reused verbatim), any holder of a valid `(raw_body, hmac)` pair — which every merchant installing the app can trivially obtain by triggering the webhook on their own store, since the HMAC secret (`Context.api_secret_key`) is the same app-wide secret for every shop — can resubmit that exact body/HMAC combination to the app's webhook endpoint with a different `x-shopify-shop-domain` (and `x-shopify-topic`) header. `Utils::HmacValidator.validate` will report the signature as valid because it never examines the header values, and `Registry.process` will pass this forged `shop` straight to `WebhookMetadata`/the registered handler.

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is supposed to enforce: an app's webhook handler (built on this gem's guarantee that `Utils::HmacValidator.validate` authenticates the whole request) will process attacker-supplied data under a victim shop's identity. Any handler that uses `data.shop` to select session state, write per-tenant records, or drive privileged flows (e.g. GDPR redaction handlers, uninstall cleanup, inventory/order sync) can be tricked into acting on an arbitrary merchant's `shop` domain with attacker-chosen body content, constituting cross-tenant access/data confusion — Critical per the rubric.

### Likelihood Explanation
Exploitation only requires the attacker to control one shop that has this app installed (or observe one legitimate webhook delivery for any topic with attacker-influenceable/reusable body content) and send an HTTP POST with a forged `shop-domain` header reusing the intercepted/self-generated valid `(body, hmac)` pair — no access to `client_secret`, access tokens, or TLS interception is required. This is reachable purely through the gem's documented webhook-processing API (`ShopifyAPI::Webhooks::Registry.process`) with no reliance on the host app deviating from documented usage.

### Recommendation
Bind the asserted identity fields to the signature verification: either compute/verify the HMAC over a canonical string that includes `shop`, `topic`, and `webhook_id` (matching what the header purports to represent) in addition to the body, or otherwise cryptographically bind these header values before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, document and enforce that consumers must independently verify `shop` against a known/installed-shop allowlist before trusting webhook payloads scoped to that shop.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook whose body content they can predict/control (e.g. a `shop/redact` mandatory webhook, or any topic where the payload doesn't strongly bind the domain), capturing the valid `(raw_body, x-shopify-hmac-sha256)` pair sent by Shopify to the app's endpoint — this pair is valid because it was HMAC'd with the app's single `client_secret`, shared across every shop installation.
2. Attacker replays this exact HTTP request to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and adjusts `x-shopify-topic` if desired) while keeping `raw_body` and `x-shopify-hmac-sha256` unchanged.
3. `ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only [5](#0-4)  and it matches, so `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)` [6](#0-5) , causing the app to process attacker-controlled data under the victim shop's identity.

### Citations

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
