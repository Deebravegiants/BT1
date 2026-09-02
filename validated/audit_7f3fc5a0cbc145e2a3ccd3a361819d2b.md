### Title
Webhook `shop` (and other Shopify headers) are trusted without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook exclusively by validating the HMAC over the raw request body, then passes the caller-supplied `x-shopify-shop-domain` header straight through to the app's handler as the authenticated tenant identifier. Because that header is never part of the signed material, an attacker can present a genuine (HMAC-valid) body captured from a webhook fired on their own store while swapping the `shop` header to a victim shop's domain, causing the host application to process the payload as if it came from the victim tenant.

### Finding Description
`Registry.process` performs the only authentication step for incoming webhooks: [1](#0-0) 
```
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

`Utils::HmacValidator.validate` computes and compares the signature only against `to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body, while `shop`, `topic`, `api_version`, and `webhook_id` are pulled unverified from HTTP headers: [3](#0-2) 

So the binding the library implicitly claims to provide — "HMAC-valid request" ⇒ "`shop` is the tenant that produced this payload" — does not hold. The equality that should be enforced is:
`shop_bound_by_signature == request.shop`
but in reality `shop_bound_by_signature` is undefined (the signature covers only `raw_body`), so `request.shop` can be set to any value the caller supplies in the header while keeping the HMAC valid, as long as the raw body itself is unchanged.

### Impact Explanation
An attacker who installs the target app on their own Shopify store (a normal, unprivileged action) can capture a legitimate webhook delivery — body + valid `x-shopify-hmac-sha256` — for an event they control (e.g. `customers/data_request`, `app/uninstalled`, `shop/redact`, or any custom topic the app subscribes to). They can then replay that exact body/HMAC pair directly to the app's public webhook endpoint while substituting `x-shopify-shop-domain` for a victim shop. `Registry.process` accepts it as valid (HMAC checks out) and dispatches `WebhookMetadata` with `shop` set to the victim's domain. Any host-application logic that trusts `WebhookMetadata#shop` as the authenticated tenant (loading the victim's session/access token, performing GDPR redaction, deactivating the wrong shop's data, etc.) now operates against the wrong tenant using attacker-chosen — but library-endorsed — identification. This is a cross-tenant access issue stemming directly from this gem's `Webhooks::Registry`/`Webhooks::Request` design.

### Likelihood Explanation
Webhook endpoints are public HTTP(S) endpoints by design (Shopify must be able to reach them from the internet), so no special network position or credential is required, other than the attacker being able to trigger one authentic webhook on their own store to obtain a valid `(raw_body, hmac)` pair — trivial for any merchant/dev who installs the app. The only constraint is that the raw body content itself must be acceptable to the handler for the victim context (e.g., an empty-body mandatory webhook, or a body whose fields don't need to differ per shop), which is realistic for several standard Shopify topics.

### Recommendation
Bind the tenant-identifying and topic/version metadata into the value that is authenticated, not just the raw body:
- Either compute/verify the HMAC over a canonical string that includes `shop`, `topic`, and `api_version` (mirroring what `Auth::Oauth::AuthQuery` does by including all business fields in `to_signable_string`), or
- Require host applications to additionally verify `request.shop` against a known/registered shop list before trusting `WebhookMetadata#shop`, and document this requirement prominently since the library's naming (`HmacValidator.validate`) currently implies full request authentication.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and configures a webhook subscription for a topic with a static/predictable body (e.g., `customers/data_request` with minimal customer info, or any topic where body content doesn't materially change the app's tenant-scoped action).
2. Shopify delivers the webhook to the app's endpoint with headers including `x-shopify-shop-domain: attacker-shop.myshopify.com` and a valid `x-shopify-hmac-sha256` computed over the raw body using the shared `api_secret_key`.
3. Attacker captures this raw body and HMAC value (e.g., via a proxy they control, since it's their own store/traffic).
4. Attacker sends a new POST request directly to the app's public webhook endpoint with the identical raw body and `x-shopify-hmac-sha256`, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only checks the (unchanged) raw body against the HMAC.
6. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, causing the app to act on the victim tenant using attacker-controlled webhook content.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
